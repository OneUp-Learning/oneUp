from django_celery_beat.models import CrontabSchedule, PeriodicTask, PeriodicTasks
from Badges.celeryApp import app
from django.utils import timezone
from datetime import timedelta

import json
import random
from _datetime import date
from celery.bin.result import result

from celery.five import monotonic
from contextlib import contextmanager
from django.core.cache import cache

import _cffi_backend
from _datetime import datetime
from dateutil.utils import today
from billiard.connection import CHALLENGE
from oneUp.logger import logger

from django.conf import settings


LOCK_EXPIRE = 60 * 5 # lock expire in 5 minutes

@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)

def setup_periodic_badge(unique_id, badge_id, variable_index, course, period_index, number_of_top_students=None, threshold=1, operator_type='>', is_random=None):
    ''' unique_id should be the created id for periodic badge object. badge_id is the id of the badge to award students'''
    unique_str = str(unique_id)+"_badge"
    return setup_periodic_variable(unique_id, unique_str, variable_index, course, period_index, number_of_top_students=number_of_top_students, threshold=threshold, operator_type=operator_type, is_random=is_random, badge_id=badge_id)

def setup_periodic_vc(unique_id, virtual_currency_amount, variable_index, course, period_index, number_of_top_students=None, threshold=1, operator_type='>', is_random=None):
    ''' unique_id should be the created id for periodic vc object. virtual_currency_amount is the amount to award students.'''
    unique_str = str(unique_id)+"_vc"
    return setup_periodic_variable(unique_id, unique_str, variable_index, course, period_index, number_of_top_students=number_of_top_students, threshold=threshold, operator_type=operator_type, is_random=is_random, virtual_currency_amount=virtual_currency_amount)
    
def setup_periodic_leaderboard(leaderboard_id, variable_index, course, period_index, number_of_top_students=None, threshold=1, operator_type='>', is_random=None):
    ''' leaderboard_id should be the created if for periodic learderboard object'''
    unique_str = str(leaderboard_id)+"_leaderboard"
    return setup_periodic_variable(leaderboard_id, unique_str, variable_index, course, period_index, number_of_top_students=number_of_top_students, threshold=threshold, operator_type=operator_type, is_random=is_random, is_leaderboard=True, save_results=True)

def setup_periodic_variable(unique_id, unique_str, variable_index, course, period_index, number_of_top_students=None, threshold=1, operator_type='>', is_random=None,  is_leaderboard=False, badge_id=None, virtual_currency_amount=None, save_results=False):
    ''' Creates Periodic Task if not created with the provided periodic variable function and schedule.'''
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]

    periodic_task, _ = PeriodicTask.objects.get_or_create(
        name=periodic_variable['name']+'_'+unique_str,
        kwargs=json.dumps({
            'unique_id': unique_id,
            'variable_index': variable_index,
            'course_id': course.courseID,
            'period_index': period_index,
            'number_of_top_students': number_of_top_students,
            'threshold': threshold,
            'operator_type': operator_type,
            'is_random': is_random,
            'is_leaderboard': is_leaderboard,
            'badge_id': badge_id,
            'virtual_currency_amount': virtual_currency_amount,
            'save_results': save_results
        }),
        task='Badges.periodicVariables.periodic_task',
        crontab=TimePeriods.timePeriods[period_index]['schedule'],
    )
    return periodic_task
def get_periodic_variable_results(variable_index, period_index, course_id):
    ''' This function will get any periodic variable results without the use of celery.
        The time period is used for how many days/minutes to go back from now.
        Ex. Time Period: Weekly - Return results within 7 days ago
        
        Returns list of tuples: [(student, value), (student, value),...]
    '''
    from Students.models import StudentRegisteredCourses
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    time_period = TimePeriods.timePeriods[period_index]
    # Get the course object and periodic variable
    course = get_course(course_id)
    # Get all the students in this course except test students
    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    rank = []
    # Evaluate each student based on periodic variable function
    for student_in_course in students:
        rank.append(periodic_variable['function'](course, student_in_course.studentID, periodic_variable, time_period, result_only=True))
    
    return rank

def delete_periodic_task(unique_id, variable_index, award_type, course):
    ''' Deletes Periodic Task when rule or badge is deleted'''

    if award_type != "badge" and award_type != "vc" and award_type != "leaderboard":
        logger.error("Cannot delete Periodic Task Object: award_type is not 'badge' or 'vc'!!")
        return None

    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    unique_str = str(unique_id)+"_"+award_type
    PeriodicTask.objects.filter(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course.courseID)).delete()

def get_course(course_id):
    ''' Method to get the course object from course id'''
    from Instructors.models import Courses
    course = Courses.objects.get(pk=int(course_id))
    return course


@app.task(ignore_result=True)
def periodic_task(unique_id, variable_index, course_id, period_index, number_of_top_students, threshold, operator_type, is_random, is_leaderboard=False, badge_id=None, virtual_currency_amount=None, save_results=False): 
    ''' Celery task which runs based on the time period (weekly, daily, etc). This task either does one of the following
        with the results given by the periodic variable function:
            1. Takes the top number of students specified by number_of_top_students variable above a threshold
            2. Takes the students above a threshold based on students results
            3. Takes a student at random above a threshold based on students results
            4. Take all the students above a threshold
        Then awards the student(s) with a badge or virtual currency.

        If badge_id is provided the student(s) will be given a badge.
        If virtual_currency_amount is provied the student(s) will be given virtual currency.
        Threshold can be either: max, avg, or some string number

        Note: unique_id is either PeriodicBadgeID(badgeID) or VirtualCurrencyPeriodicRuleID(vcRuleID) or leaderboard id
        Note: operator_type is string, is_random is a boolean, and threshold is a string. Everything else should be an integer
        None: if number_of_top_students and is_random is null then all is assumed (see number 4)
    '''
    from Students.models import StudentRegisteredCourses, PeriodicallyUpdatedleaderboards
    from Badges.models import CourseConfigParams

    # Get the periodic variable and time period
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    time_period = TimePeriods.timePeriods[period_index]

    course = get_course(course_id)
    
    # Set the award type used for finding Periodic Task object
    award_type = ""
    if badge_id is not None:
        award_type += "badge"
    if virtual_currency_amount is not None:
        award_type += "vc"
    if is_leaderboard:
        award_type += "leaderboard"

    unique_str = str(unique_id)+"_"+award_type
    task_id = periodic_variable['name']+'_'+unique_str
    print("RUNNING PV - {} - {} - {}".format(task_id, time_period['name'], course.courseName))

    # Get the course
    today = datetime.now(tz=timezone.utc).date()
    course_config = CourseConfigParams.objects.get(courseID=course)
    if course_config.courseStartDate > today or course_config.courseEndDate < today:
        print("Today: {} Course End Date: {} Course Start Date: {}".format(today,course_config.courseEndDate,course_config.courseStartDate ))
        periodic_task = PeriodicTask.objects.get(name=task_id, kwargs__contains='"course_id": '+str(course_id))
        periodic_task.delete()
        print("DELETE OLD PV - {} - {} - {}".format(task_id, time_period['name'], course.courseName))
        return

    # Aquire the lock for the task 
    lock_id = "lock-{}".format(task_id)
    with memcache_lock(lock_id, app.oid) as acquired:
        if not acquired:
            print("NO LOCK PV - {} - {} - {}".format(task_id, time_period['name'], course.courseName))
            return
    
    periodic_task = PeriodicTask.objects.get(name=task_id, kwargs__contains='"course_id": '+str(course_id))
    total_runs = periodic_task.total_run_count
    print("TOTAL RUNS {} ({})".format(total_runs, task_id))
    # Handle beginning of time period
    if time_period == TimePeriods.timePeriods[TimePeriods.beginning_of_time]:
        # If it has ran once then return and set it not to run anymore
        if total_runs >= 1:
            periodic_task.enabled = False
            periodic_task.save()
            PeriodicTasks.changed(periodic_task)
            print("END COMPLETE PV - {} - {} - {}".format(task_id, time_period['name'], course.courseName))
            return
    # Check for frequency to see handle every N days/month/week etc
    # ex. biweekly
    # (day 1) total_runs = 0 , frequency = 2, task will run
    # (day 7) total_runs = 1 , frequency = 2, task will not run
    # (day 14) total_runs = 2 , frequency = 2, task will run
    # ...
    
    if total_runs % time_period['frequency'] != 0:
        print("SKIP PV - {} - {} - {}".format(task_id, time_period['name'], course.courseName))
        periodic_task.total_run_count += 1
        periodic_task.save()
        PeriodicTasks.changed(periodic_task)
        return

    # Get all the students in this course, exclude test student
    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    rank = []
    last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    # Evaluate each student based on periodic variable function
    for student_in_course in students:
        rank.append(periodic_variable['function'](course, student_in_course.studentID, periodic_variable, time_period, last_ran = last_ran, unique_id=unique_id, award_type=award_type))

    # Set this as the last time this task has ran
    set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)

    print("Results: {}".format(rank))
    # Filter out students based on periodic badge/vc rule settings
    if not is_leaderboard and not save_results:
        rank = filter_students(rank, number_of_top_students, threshold, operator_type, is_random)
        print("Final Filtered ({}, {}, {}, {}): {}".format(number_of_top_students, threshold, operator_type, is_random, rank))
        # Give award to students
        award_students(rank, course, unique_id, badge_id, virtual_currency_amount)
    elif save_results:
        if is_leaderboard:
            # Get top n students and save to leaderboard
            rank = filter_students(rank, number_of_top_students+1, 0, '>=', False)
            print("Final Filtered Leaderboard ({}, {}, {}, {}): {}".format(number_of_top_students+1, 0, '>=', False, rank))
            savePeriodicLeaderboardResults(rank, unique_id, course)
              
    periodic_task.total_run_count += 1
    periodic_task.save()
    PeriodicTasks.changed(periodic_task)

    # Create/update celery log so it can be used for a fallback option if this task didn't run on time
    update_celery_log_entry(task_id, {
        'unique_id': unique_id,
        'variable_index': variable_index,
        'course_id': course_id,
        'period_index': period_index,
        'number_of_top_students': number_of_top_students,
        'threshold': threshold,
        'operator_type': operator_type,
        'is_random': is_random,
        'is_leaderboard': is_leaderboard,
        'badge_id': badge_id,
        'virtual_currency_amount': virtual_currency_amount,
        'save_results': save_results
    })

    print("END COMPLETE PV - {} - {} - {}".format(task_id, time_period['name'], course.courseName))

def update_celery_log_entry(task_id, parameters):
    ''' Create/update celery log so it can be used for a fallback option if this task didn't run on time '''
    from Badges.models import CeleryTaskLog
    
    celery_log_entry = CeleryTaskLog.objects.filter(taskID=task_id).first()
    if celery_log_entry is None:
        # Create new celery log entry
        celery_log_entry = CeleryTaskLog()
        celery_log_entry.taskID = task_id

    celery_log_entry.parameters = json.dumps(parameters)
    celery_log_entry.save()

def filter_students(students, number_of_top_students, threshold, operator_type, is_random):
    ''' Filters out students based on parameters if they are not None.
        number_of_top_students: gets the top number of students wanted
        threshold & operator_type: gets the students which are above/at a threshold
                                    threshold can be a value or a string (max, avg, etc)
        is_random: randomly chooses a student. Can be paired with threshold.
    '''

    if students:
        operatorType = {
            '>=': lambda x, y : x >= y,
            '>' : lambda x, y : x > y,
            '=' : lambda x, y : x == y
        }
        # Filter students based on if their result passes the threshold
        if not threshold in ['avg', 'max']:
            students = [(student, val) for student, val in students if operatorType[operator_type](val, int(threshold))]
        else:
            if threshold == 'max':
                max_val = max(students, key=lambda item:item[1])[1]
                # If the max value is 0 or less then we should not award any students
                if max_val <= 0:
                    students = []
                    return students

                students = [(student, val) for student, val in students if operatorType[operator_type](val, max_val)]
            elif threshold == 'avg':
                avg = round(sum([val for _, val in students])/len(students), 1)
                students = [(student, val) for student, val in students if operatorType[operator_type](val, avg)]

        if number_of_top_students and students:
            # Sort the students
            students.sort(key=lambda tup: tup[1], reverse=True)
            # Check if what we want is greater than the number of students
            if len(students) >= number_of_top_students:
                # Get the top n (number_of_top_students) unique values to handle ties
                top_values = sorted(set([val for student, val in students]), reverse=True)
                top_values = top_values[:number_of_top_students]
                # Only select the students if their value is in the top_values
                students = [(student, val) for student, val in students if val in top_values]
        elif is_random and students:
            # If random, choose one student and remove everyone else
            random.shuffle(students)
            students = random.sample(students, 1)
    return students

def award_students(students, course, unique_id, badge_id=None, virtual_currency_amount=None):
    ''' Awards students a badge or virtual currency or both.'''

    from notify.signals import notify  
    from Students.models import StudentBadges, StudentRegisteredCourses, StudentVirtualCurrency
    from Badges.models import BadgesInfo, VirtualCurrencyPeriodicRule
    from Instructors.views.utils import utcDate

    for student, result in students:
        # Give award for either badge or virtual currency
        if badge_id:
            # Check if student has earned this badge
            studentBadges = StudentBadges.objects.filter(studentID = student, badgeID = badge_id)

            # If the badge has not already been earned, then award it 
            badge = BadgesInfo.objects.get(pk=badge_id)
   
            studentBadge = StudentBadges()
            studentBadge.studentID = student
            studentBadge.badgeID = badge
            studentBadge.objectID = 0
            studentBadge.timestamp = utcDate() - timedelta(hours=4)
            studentBadge.save()
            
            # Notify student of badge award 
            notify.send(None, recipient=student.user, actor=student.user, verb='You won the '+badge.badgeName+' badge', nf_type='Badge', extra=json.dumps({"course": str(course.courseID)}))
            
        # Give award of virtual currency
        if virtual_currency_amount:
            if virtual_currency_amount > 0:
                student_profile = StudentRegisteredCourses.objects.get(courseID=course, studentID=student)
                student_profile.virtualCurrencyAmount += virtual_currency_amount
                student_profile.save()
                
                periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)

                transaction = StudentVirtualCurrency()
                transaction.courseID = course
                transaction.studentID = student
                transaction.objectID = 0
                transaction.vcName = periodicVC.vcRuleName
                transaction.vcDescription = periodicVC.vcRuleDescription
                transaction.value = virtual_currency_amount
                transaction.save()
                # Notify student of VC award 
                notify.send(None, recipient=student.user, actor=student.user, verb='You won '+str(virtual_currency_amount)+' course bucks', nf_type='Increase VirtualCurrency', extra=json.dumps({"course": str(course.courseID)}))

def get_last_ran(unique_id, variable_index, award_type, course_id):
    ''' Retrieves the last time a periodic task has ran. 
        Returns None if it is has not ran yet.
    '''
    # print("award type", award_type)
    if not "badge" in award_type  and not "vc" in award_type and not "leaderboard" in award_type:
        logger.error("Cannot find Periodic Task Object: award_type is not 'badge' or 'vc' or 'leaderboard'!!")
        return None

    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    unique_str = str(unique_id)+"_"+award_type

    last_ran = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id)).last_run_at
    return last_ran

def set_last_ran(unique_id, variable_index, award_type, course_id):
    ''' Sets periodic task last time ran datefield. It is not updated accurately by itself.'''
    from Instructors.views.utils import utcDate
    if not "badge" in award_type  and not "vc" in award_type and not "leaderboard" in award_type:
        logger.error("Cannot find Periodic Task Object: award_type is not 'badge' or 'vc' or 'leaderboard'!!")
        return None

    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    unique_str = str(unique_id)+"_"+award_type

    task = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id))
    task.last_run_at = utcDate()
    task.save()
    PeriodicTasks.changed(task)

def savePeriodicLeaderboardResults(rank,leaderboardConfigID,course):
    #"saving results", rank, leaderboardConfigID, course)
    from Students.models import PeriodicallyUpdatedleaderboards
    from Badges.models import LeaderboardsConfig
  
    leaderboardConfigID = LeaderboardsConfig.objects.get(leaderboardID=int(leaderboardConfigID))
    #"leaderboardConfigID", leaderboardConfigID)
    #"rank", rank)
   
    #we must filter out the test student
    studentsPlusScores = []
    for student in rank:
        if not student[0].isTestStudent:
            studentsPlusScores.append(student)
    index = 1
    
    studentsWithoutZeroes = []
    #filter out the zero point scores if any
    for student in studentsPlusScores:
        if student[1] != 0 or student[1] != 0.0:
            studentsWithoutZeroes.append(student)
    
    studentsPlusScores = studentsWithoutZeroes
    #iterate over the list of studentsplusscores and make the records or update existing records
    for student in studentsPlusScores:
        #"currentStudent", student,"index" ,index)
        leaderboardRecord = PeriodicallyUpdatedleaderboards.objects.filter(leaderboardID=int(leaderboardConfigID.leaderboardID), studentID=student[0])
        #"leaderboard", leaderboardRecord)
        
        if leaderboardRecord:
            #we have a record so we should update", leaderboardRecord[0])
            leaderboard = leaderboardRecord[0]
            leaderboard.studentID = student[0]
            leaderboard.studentPoints = student[1]
            leaderboard.studentPosition = index
        else:
            #"creating a new one since we dont have a record for"
            leaderboard = PeriodicallyUpdatedleaderboards()
            leaderboard.leaderboardID = leaderboardConfigID
            leaderboard.studentID = student[0]
            leaderboard.studentPoints = student[1]
            leaderboard.studentPosition = index
        leaderboard.save()
        index = index + 1
    #remaining records should be set to zero   
    leaderboardRecords = PeriodicallyUpdatedleaderboards.objects.filter(leaderboardID=int(leaderboardConfigID.leaderboardID), studentID=student[0])  
    if index <= len(leaderboardRecords):
        for leaderboard in leaderboardRecords[index:]:
            #"setting -1 to records after our index, no student can be -1")
            leaderboard.studentPosition = -1
            leaderboard.save()

def calculate_student_earnings(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    ''' This calculates the student earnings of virtual currency since the last period.
        Earnings are defined by only what virtual currency they gained and not spent.'''
    
    print("Calculating Highest Earner") 
    from Students.models import StudentVirtualCurrency
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule, LeaderboardsConfig

    if result_only:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None

    # Get the earnings for this student
    earnings = StudentVirtualCurrency.objects.filter(studentID = student, courseID = course)
    # If this is not the first time running, only get the earnings since last ran
    if last_ran:
        earnings = earnings.filter(timestamp__gte=last_ran)
    elif not result_only:
        # Set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous earnings from beginning of time
        if award_type == 'badge':
            periodic_badge = PeriodicBadges.objects.get(badgeID=unique_id, courseID=course)
            earnings = earnings.filter(timestamp__gte=periodic_badge.lastModified)
        elif award_type == 'vc':
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)
            earnings = earnings.filter(timestamp__gte=periodicVC.lastModified)
        elif award_type == 'leaderboard':
            periodic_leaderboard =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course)
            earnings = earnings.filter(timestamp__gte=periodic_leaderboard.lastModified)
    
    # Get the total earnings only if they have earned more than 0
    total = sum([int(earn.value) for earn in earnings if earn.value > 0])
   
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(total))

    return (student, total)

def calculate_student_warmup_practice(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    ''' This calculates the number of times the student has practiced Warm-up challenges. This includes the
        number of times the student has completed the same challenge.
        Ex. Warm-up Challenge A: practiced 10 times
            Warm-up Challenge B: practice 2 times
            Total practiced: 12 times
    '''
    
    print("Calculating Student Practice") 
    from Instructors.models import Challenges
    from Students.models import StudentChallenges
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule, LeaderboardsConfig
   
    # Check aganist only Warm-up challenges
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    # The amount of times the student has practice Warm-up challenges
    practices = 0

    # If theere are no Warm-up challenges then we just say the student didn't practice anything :)
    if not challenges.exists():
        return (student, practices)
    
    # If this is first time running, set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous challenges from beginning of time
    if not last_ran:
        if award_type == 'badge':
            periodic_badge = PeriodicBadges.objects.get(badgeID=unique_id, courseID=course)
            last_ran = periodic_badge.lastModified
        elif award_type == 'vc':
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)
            last_ran = periodicVC.lastModified
        elif award_type == 'leaderboard':
            periodic_leaderboard =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course)
            last_ran = periodic_leaderboard.lastModified
        elif result_only:
            date_time = time_period['datetime']
            if date_time:
                last_ran = date_time()
            else:
                last_ran = None

    for challenge in challenges:
        # Get the student completed Warm-up challenges (Endtimestamp is not null if it is complete)
        studentChallenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge.challengeID).exclude(endTimestamp__isnull=True)
        # Only get the student challenges since last ran
        if last_ran:
            studentChallenges = studentChallenges.filter(endTimestamp__gte=last_ran)           

        if studentChallenges.exists():
            print("Student Challenges: {}".format(studentChallenges))
            practices += len(studentChallenges)

    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Practices: {}".format(practices))

    return (student, practices)

def calculate_number_of_days_of_unique_warmups(course, student, periodic_variable, time_period, percentage, last_ran=None, unique_id=None, award_type=None, result_only=False):
    ''' Utility function for getting the number of days of unique warmup challenges that a student completed with a score > percentage'''

    print("Calculating number of days of unique warmups completed with score > {}%".format(percentage))
    from Instructors.models import Challenges
    from Students.models import StudentChallenges
    from decimal import Decimal
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    
    # Check against only Warm-up challenges
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    
    # The amount of days
    days = 0

    # If there are no Warm-up challenges then we just say the student didn't complete anything
    if not challenges.exists():
        return (student, days)
    
    # If this is first time running, set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous challenges from beginning of time
    if not last_ran:
        if award_type == 'badge':
            periodic_badge = PeriodicBadges.objects.get(badgeID=unique_id, courseID=course)
            last_ran = periodic_badge.lastModified
        elif award_type == 'vc':
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)
            last_ran = periodicVC.lastModified
        elif award_type == 'leaderboard':
            periodic_leaderboard =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course)
            last_ran = periodic_leaderboard.lastModified
        elif result_only:
            date_time = time_period['datetime']
            if date_time:
                last_ran = date_time()
            else:
                last_ran = None

    for challenge in challenges:
        # Get the student completed Warm-up challenges (Endtimestamp is not null if it is complete)
        studentChallenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge.challengeID).exclude(endTimestamp__isnull=True)
        # Only get the student challenges since last ran
        if last_ran:
            studentChallenges = studentChallenges.filter(endTimestamp__gte=last_ran)

        if studentChallenges.exists():
            # Get the total possible score (Note: total score is Decimal type) for this challenge
            total_score_possible = challenge.getCombinedScore()
            # Get the highest score out of the student attempts for this challenge (Note: test score is Decimal type)
            highest_score = max([warmup.getScore() for warmup in studentChallenges])
            print("Highest score: {}".format(highest_score))
            print("possible score {}".format(total_score_possible))

            # If the total possible score is not set then skip this Warm-up challenge
            if total_score_possible <= 0:
                continue
            # Calculate the percentage
            student_percentage = (highest_score/total_score_possible) * Decimal(100)
            print("student percentage {}".format(student_percentage))
            print("percentage {}".format(Decimal(percentage)))
            # Say this challenge is counted for if the student score percentage is greater than 80%
            if student_percentage > Decimal(percentage):
                days += 1

    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Unique Warm-ups: {}".format(days))
    return (student, days)

def calculate_number_of_days_of_unique_warmups_greater_than_90(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    ''' This will return the number of days of unique warmup challenges that a student completed with a 
        score > 70%'''

    return calculate_number_of_days_of_unique_warmups(course, student, periodic_variable, time_period, 90.0, last_ran, unique_id, award_type, result_only)

def calculate_number_of_days_of_unique_warmups_greater_than_70(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    ''' This will return the number of days of unique warmup challenges that a student completed with a 
        score > 90%'''

    return calculate_number_of_days_of_unique_warmups(course, student, periodic_variable, time_period, 70.0, last_ran, unique_id, award_type, result_only)

def calculate_unique_warmups(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    ''' This calculates the number of unique Warm-up challenges the student has completed
        with a score greater than 70%.
    '''
    print("Calculating Unique Warmups with a Score > 70%") 
    from Instructors.models import Challenges
    from Students.models import StudentChallenges
    from decimal import Decimal
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
      
    # Check aganist only Warm-up challenges
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    # The amount of unique Warm-up challenges with a score greater than 60%
    unique_warmups = 0

    # If theere are no Warm-up challenges then we just say the student didn't complete anything
    if not challenges.exists():
        return (student, unique_warmups)
    
    # If this is first time running, set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous challenges from beginning of time
    if not last_ran:
        if award_type == 'badge':
            periodic_badge = PeriodicBadges.objects.get(badgeID=unique_id, courseID=course)
            last_ran = periodic_badge.lastModified
        elif award_type == 'vc':
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)
            last_ran = periodicVC.lastModified
        elif award_type == 'leaderboard':
            periodic_leaderboard =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course)
            last_ran = periodic_leaderboard.lastModified
        elif result_only:
            date_time = time_period['datetime']
            if date_time:
                last_ran = date_time()
            else:
                last_ran = None

    for challenge in challenges:
        # Get the student completed Warm-up challenges (Endtimestamp is not null if it is complete)
        studentChallenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge.challengeID).exclude(endTimestamp__isnull=True)
        # Only get the student challenges since last ran
        if last_ran:
            studentChallenges = studentChallenges.filter(endTimestamp__gte=last_ran)

        if studentChallenges.exists():
            print("Student Challenges: {}".format(studentChallenges))
            # Get the total possible score (Note: total score is Decimal type) for this challenge
            total_score_possible = challenge.getCombinedScore()
            # Get the highest score out of the student attempts for this challenge (Note: test score is Decimal type)
            highest_score = max([warmup.getScore() for warmup in studentChallenges])
            # If the total possible score is not set then skip this Warm-up challenge
            if total_score_possible <= 0:
                continue
            # Calculate the percentage
            percentage = (highest_score/total_score_possible) * Decimal(100)
            # Say this challenge is counted for if the student score percentage is greater than 70%
            if percentage > Decimal(70.0):
                unique_warmups += 1

    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Unique Warm-ups: {}".format(unique_warmups))

    return (student, unique_warmups)
def streakProvider(unique_id, course, student, streakTypeNum):
    from Students.models import StudentStreaks
    if StudentStreaks.objects.filter(courseID=course.courseID, studentID=student, streakType=streakTypeNum).exists():
        studentStreak = StudentStreaks.objects.filter(courseID=course.courseID, studentID=student)[0]
    else:
        studentStreak = StudentStreaks()
        studentStreak.studentID = student
        studentStreak.courseID = course
        studentStreak.streakStartDate = datetime.now().strftime("%Y-%m-%d")
        studentStreak.streakType = streakTypeNum
        studentStreak.objectID = unique_id
        studentStreak.currentStudentStreakLength = 0
    return studentStreak

def calculate_student_attendance_streak(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    print("Calculating student_attendance_streak") 
    #this one is best ran with daily time period
    #weekly will work but cause it to ignore the extra attendance days unless set up properly.
    #should be set before the start of a week, week defined as 7 days. 
    from Students.models import StudentStreaks, StudentAttendance
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule, CourseConfigParams
    from Instructors.models import AttendanceStreakConfiguration
    from datetime import datetime, timedelta
    import ast
            
    threshold = 0
    resetStreak = False
    streakTypeNum = None
    #if detemine which type of award this is and obtain thresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            threshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
            streakTypeNum = 0
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            threshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
            streakTypeNum = 1

    studentStreak = streakProvider(unique_id, course, student, streakTypeNum)
        
    
    # Get the attendance for this student
    if AttendanceStreakConfiguration.objects.filter(courseID=course.courseID).exists():
        print("attendance exists")
        
        #determine the days of class for our entire class
        streak = AttendanceStreakConfiguration.objects.filter(courseID=course.courseID)[0]
        excluded_Dates = streak.daysDeselected
        streakDays = ast.literal_eval(streak.daysofClass)
        streakDays = [int(i) for i in streakDays]
        streak_calendar_days = []
        ccparams = CourseConfigParams.objects.get(courseID=course.courseID)
        d = ccparams.courseStartDate
        while d <= ccparams.courseEndDate:
            if d.weekday() in streakDays:
                streak_calendar_days.append(d.strftime("%Y-%m-%d"))
            d += timedelta(days=1)
        events = []
        filteredStreakDays = []
        for date in streak_calendar_days:
            if date not in excluded_Dates:
                filteredStreakDays.append(date)
        isTodayStreakDay = False
        if datetime.now().strftime("%Y-%m-%d") in filteredStreakDays:
            isTodayStreakDay = True
            

    student_total = 0
    # Cases when threshold is passed as max or avg or as number
    # Need to calculate the avg of all students totals and find max of all students

    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    max_total = 0
    avg_total = 0
    for s in students:
        stud = s.studentID
        total = 0
        if StudentAttendance.objects.filter(courseID=course.courseID, studentID=stud, timestamp=datetime.now().strftime("%Y-%m-%d")).exists():
            if StudentStreaks.objects.filter(courseID=course.courseID, studentID=stud, streakType=0).exists():
                streak = StudentStreaks.objects.filter(courseID=course.courseID, studentID=stud)[0]
                total = streak.currentStudentStreakLength + 1
                
        # Set max
        if total > max_total:
            max_total = total

        # Sum to find avg
        avg_total += total

        # Set the student total that this calculation should be run for
        if stud == student:
            student_total = total
        
    
    avg_total = avg_total / len(students)

    # Determine the threshold value 
    if threshold == 'max':
        threshold = max_total
    elif threshold == 'avg':
        threshold = avg_total
    else:
        threshold = int(threshold)

    if isTodayStreakDay:
        
        if StudentAttendance.objects.filter(courseID=course.courseID, studentID=student, timestamp=datetime.now().strftime("%Y-%m-%d")).exists():
            studentStreak.currentStudentStreakLength += 1
            student_total = studentStreak.currentStudentStreakLength
            
            #if total is larger than streak and we want to NOT reset streak
            if student_total > threshold and resetStreak:
                studentStreak.currentStudentStreakLength = 0
                student_total = threshold
            elif student_total > threshold and not resetStreak:
                if student_total % threshold == 0:
                    student_total = threshold
                else:
                    #student_total is set as remainder of current streak length and threshold
                    student_total %= threshold
            elif student_total == threshold and resetStreak:
                studentStreak.currentStudentStreakLength = 0
                student_total = threshold
            elif student_total == threshold and not resetStreak:
                student_total = threshold
                
        else:
            studentStreak.currentStudentStreakLength = 0
            student_total = 0
                        
    studentStreak.save()
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(student_total))

    return (student, student_total)

def calculate_student_xp_rankings(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id, last_ran=last_ran, result_only=result_only, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, award_type=award_type)
    
def calculate_warmup_rankings(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id, last_ran=last_ran, result_only=result_only, gradeWarmup=True, gradeSerious=False, seriousPlusActivity=False, award_type=award_type)
    
def calculate_serious_challenge_rankings(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id, last_ran=last_ran, result_only=result_only, gradeWarmup=False, gradeSerious=True, seriousPlusActivity=False, award_type=award_type)
    
def calculate_serious_challenge_and_activity_rankings(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id , last_ran=last_ran, result_only=result_only, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=True, award_type=award_type)

def calculate_student_challenge_streak(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type="leaderboard", result_only=False):
    print("Calculating student challenge streak") 
    from Students.models import StudentStreaks, StudentChallenges
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    from datetime import datetime

    if result_only:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None
           
    threshold = 0
    resetStreak = False 
    streakTypeNum = None
    #if detemine which type of award this is and obtain thresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            threshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
            streakTypeNum = 0
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            threshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
            streakTypeNum = 1
     
    studentStreak = streakProvider(unique_id, course, student, streakTypeNum)  

    student_total = 0
    # Cases when threshold is passed as max or avg or as number
    # Need to calculate the avg of all students totals and find max of all students

    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    max_total = 0
    avg_total = 0
    for s in students:
        stud = s.studentID
        total = 0
        challengeCount = len(StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d"))))
        #figure out how many challenges have been completed by the student
        if StudentStreaks.objects.filter(courseID=course.courseID, studentID=stud, streakType=0).exists():
            streak = StudentStreaks.objects.filter(courseID=course.courseID, studentID=stud)[0]
            total = streak.currentStudentStreakLength + challengeCount
        else:
            total = challengeCount
        
        # Set max
        if total > max_total:
            max_total = total

        # Sum to find avg
        avg_total += total

        # Set the student total that this calculation should be run for
        if stud == student:
            student_total = total
    
    avg_total = avg_total / len(students)

    # Determine the threshold value 
    if threshold == 'max':
        threshold = max_total
    elif threshold == 'avg':
        threshold = avg_total
    else:
        threshold = int(threshold)



    #if total is larger than streak and we want to NOT reset streak
    if student_total > threshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        student_total = threshold
    elif student_total > threshold and not resetStreak:
        if student_total % threshold == 0:
            student_total = threshold
        else:
            #total is set as remainder of current streak length and threshold
            student_total %= threshold
    elif student_total == threshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        student_total = threshold
    elif student_total == threshold and not resetStreak:
        student_total = threshold
        
    studentStreak.save()
    
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(student_total))

    
    return (student, student_total)

def getPercentageScoreForStudent(challengeID, student, percentage, last_ran):
    from Students.models import StudentStreaks, StudentChallenges
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    from datetime import datetime
    from Instructors.models import Challenges
    challengeTotalScore = 0
    studentScores = []
    filteredStudentScores = []
    maxStudentScore = 0

    challengeID = challengeID.challengeID
    print("percentage", percentage)
    if Challenges.objects.filter(challengeID= challengeID).exists():
        challengeTotalScore = Challenges.objects.filter(challengeID= challengeID)[0].totalScore
    
    if StudentChallenges.objects.filter(challengeID=challengeID, studentID=student, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d"))).exists():
        studentChallenges = StudentChallenges.objects.filter(challengeID=challengeID, studentID=student)
        for studentChallenge in studentChallenges:
            studentScores.append(float((studentChallenge.testScore/challengeTotalScore)))
        filteredStudentScores = list(filter(lambda x: x >= percentage, studentScores))
        print("filteredStudentScores", filteredStudentScores)
    if filteredStudentScores:
        return 1
    else:
        return 0

def calculate_student_challenge_streak_for_percentage(percentage, course, student, periodic_variable, time_period, last_ran, unique_id, award_type, result_only):
    print("Calculating student challenge >= streak") 
    from Students.models import StudentStreaks, StudentChallenges, StudentRegisteredCourses
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    from datetime import datetime
    from Instructors.models import Challenges

    percentage = percentage *.01
    # Check aganist only Warm-up challenges
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    # The amount of unique Warm-up challenges with a score greater than 60%
    unique_warmups = 0
    
    # If this is first time running, set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous challenges from beginning of time
    if last_ran == None:
        if award_type == 'badge':
            periodic_badge = PeriodicBadges.objects.get(badgeID=unique_id, courseID=course)
            last_ran = periodic_badge.lastModified
        elif award_type == 'vc':
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)
            last_ran = periodicVC.lastModified

    if result_only:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None
           
    threshold = 0
    resetStreak = False
    streakTypeNum = None
    #if detemine which type of award this is and obtain thresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            threshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
            streakTypeNum = 0
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            threshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
            streakTypeNum = 1
     
    studentStreak = streakProvider(unique_id, course, student, streakTypeNum)   
                
    student_total = 0
    # Cases when threshold is passed as max or avg or as number
    # Need to calculate the avg of all students totals and find max of all students

    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    max_total = 0
    avg_total = 0
    for s in students:
        stud = s.studentID
        total = 0
        challengeCount = len(StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d"))))
        studentChallengeIDs = []
        maxScores = []

        if challengeCount > 1:
            studentChallenges = StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d")))
            for challenge in studentChallenges:
                studentChallengeIDs.append(challenge.challengeID)
            challengeScores = []
            for studentChallengeID in studentChallengeIDs:
                if getPercentageScoreForStudent(studentChallengeID, stud, percentage, last_ran):
                    total += 1
        elif challengeCount == 1:
            studentChallenge = StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID,
            endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d")))[0]
            challenge = Challenges.objects.filter(challengeID=studentChallenge.challengeID)[0]
            if (studentChallenge.testScore/challenge.challengeTotalScore) >= (percentage):
                total += 1

        
        # Set max
        if total > max_total:
            max_total = total

        # Sum to find avg
        avg_total += total

        # Set the student total that this calculation should be run for
        if stud == student:
            student_total = total
    
    avg_total = avg_total / len(students)

    # Determine the threshold value 
    if threshold == 'max':
        threshold = max_total
    elif threshold == 'avg':
        threshold = avg_total
    else:
        threshold = int(threshold)

    #if total is larger than streak and we want to NOT reset streak
    if student_total > threshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        student_total = threshold
    elif student_total > threshold and not resetStreak:
        if student_total % threshold == 0:
            student_total = threshold
        else:
            #total is set as remainder of current streak length and threshold
            student_total %= threshold
    elif student_total == threshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        student_total = threshold
    elif student_total == threshold and not resetStreak:
        student_total = threshold
        
    studentStreak.save()
    
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(student_total))

    
    return (student, student_total)
    
def calculate_student_challenge_streak_for_percentage_over_span_of_days(percentage, course, student, periodic_variable, time_period, last_ran, unique_id, award_type, result_only):
    from Students.models import StudentStreaks, StudentChallenges
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    from datetime import datetime
    from Instructors.models import Challenges

    percentage = percentage *.01
    # Check aganist only Warm-up challenges
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    # The amount of unique Warm-up challenges with a score greater than 60%
    unique_warmups = 0
    
    # If this is first time running, set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous challenges from beginning of time
    if last_ran == None:
        if award_type == 'badge':
            periodic_badge = PeriodicBadges.objects.get(badgeID=unique_id, courseID=course)
            last_ran = periodic_badge.lastModified
        elif award_type == 'vc':
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=unique_id, courseID=course)
            last_ran = periodicVC.lastModified
    
    if result_only:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None
           
    threshold = 0
    resetStreak = False
    streakTypeNum = None
    #if detemine which type of award this is and obtain thresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            threshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
            streakTypeNum = 0
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            threshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
            streakTypeNum = 1
     
    studentStreak = streakProvider(unique_id, course, student, streakTypeNum) 
        
    student_total = 0
    # Cases when threshold is passed as max or avg or as number
    # Need to calculate the avg of all students totals and find max of all students

    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    max_total = 0
    avg_total = 0
    for s in students:
        stud = s.studentID
        total = 0
        challengeCount = len(StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d"))))
        studentChallengeIDs = []
        maxScores = []

        if challengeCount > 1:
            studentChallenges = StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d")))
            for challenge in studentChallenges:
                studentChallengeIDs.append(challenge.challengeID)
            challengeScores = []
            for studentChallengeID in studentChallengeIDs:
                if getPercentageScoreForStudent(studentChallengeID, stud, percentage, last_ran):
                    total += 1
        elif challengeCount == 1:
            studentChallenge = StudentChallenges.objects.filter(studentID=stud, courseID=course.courseID,
            endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d")))[0]
            challenge = Challenges.objects.filter(challengeID=studentChallenge.challengeID)[0]
            if (studentChallenge.testScore/challenge.challengeTotalScore) >= (percentage):
                total += 1

        # Set max
        if total > max_total:
            max_total = total

        # Sum to find avg
        avg_total += total

        # Set the student total that this calculation should be run for
        if stud == student:
            student_total = total
    
    avg_total = avg_total / len(students)

    # Determine the threshold value 
    if threshold == 'max':
        threshold = max_total
    elif threshold == 'avg':
        threshold = avg_total
    else:
        threshold = int(threshold)

    if student_total:
        studentStreak.currentStudentStreakLength = 0
    else:
        studentStreak.currentStudentStreakLength += 1

    #if total is larger than streak and we want to NOT reset streak
    if studentStreak.currentStudentStreakLength >= threshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        student_total = threshold
    elif studentStreak.currentStudentStreakLength >= threshold and not resetStreak:
        student_total = threshold
    elif studentStreak.currentStudentStreakLength == threshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        student_total = threshold
    elif studentStreak.currentStudentStreakLength == threshold and not resetStreak:
        student_total = threshold
        
    studentStreak.save()
    
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(student_total))

    
    return (student, student_total)

def calculate_warmup_challenge_greater_or_equal_to_70(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return calculate_student_challenge_streak_for_percentage(70,course, student, periodic_variable, time_period, last_ran, unique_id, award_type, result_only)

def calculate_warmup_challenge_greater_or_equal_to_40(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return calculate_student_challenge_streak_for_percentage(40,course, student, periodic_variable, time_period, last_ran, unique_id, award_type, result_only)

def calculate_warmup_challenge_greater_or_equal_to_70_by_day(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return calculate_student_challenge_streak_for_percentage_over_span_of_days(70,course, student, periodic_variable, time_period, last_ran, unique_id, award_type, result_only)

def calculate_warmup_challenge_greater_or_equal_to_40_by_day(course, student, periodic_variable, time_period, last_ran=None, unique_id=None, award_type=None, result_only=False):
    return calculate_student_challenge_streak_for_percentage_over_span_of_days(40,course, student, periodic_variable, time_period, last_ran, unique_id, award_type, result_only)
                
def studentScore(studentId, course, periodic_variable, time_period, unique_id, last_ran=None, result_only=False,gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, context_dict = None, award_type=None):
    
    from Badges.models import CourseConfigParams, LeaderboardsConfig
    from Instructors.models import Challenges, Activities, CoursesSkills, Skills
    from Students.models import StudentChallenges, StudentActivities, StudentCourseSkills
    from Students.views import classResults

    xp = 0  
    xpWeightSP = 0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    ccparamsList = CourseConfigParams.objects.filter(courseID=course)
    
    # If result only, we only want to search from the start of the course
    # else, we will search based on howFarBack (see below)
    if result_only:
        date_time = time_period['datetime']
        date_time = date_time()
        startOfTime = True
            
    else:
        date_time = last_ran 
        
        if not date_time:
            periodic_leaderboard =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course.courseID)
            backwardsTime = periodic_leaderboard.howFarBack
            
            if backwardsTime == 1500:
                date_time = date.today() - timedelta(1)
                
            elif backwardsTime == 1501:
                date_time = date.today() - timedelta(7)
                
            else:
                date_time = None
            
        # set_last_ran(unique_id, periodic_variable['index'], "leaderboard", course.courseID)
        startOfTime = False
        
    
    
    print("Course: {}".format(course))
    print("Student: {}".format(studentId))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(date_time))
    
    # Specify if the xp should be calculated based on max score or first attempt
    xpSeriousMaxScore = True 
    xpWarmupMaxScore = True
    if len(ccparamsList) >0:
        cparams = ccparamsList[0]
        xpWeightSP=cparams.xpWeightSP
        xpWeightSChallenge=cparams.xpWeightSChallenge
        xpWeightWChallenge=cparams.xpWeightWChallenge
        xpWeightAPoints=cparams.xpWeightAPoints
        xpSeriousMaxScore = cparams.xpCalculateSeriousByMaxScore 
        xpWarmupMaxScore = cparams.xpCalculateWarmupByMaxScore 

    ###
    ### The last parameter, context_dict, was added to provide the extra 
    ### information needed by acheievementsView.py for the achievements page.
    ### One may want to exclude the last parameter when calling this function 
    ### for calculating only xp.
    ### Oumar
    ###
    if not context_dict is None:
        cparams = ccparamsList[0]
        context_dict['badgesUsed'] = str(cparams.badgesUsed)
        context_dict['levelingUsed'] = str(cparams.levelingUsed)
        context_dict['leaderboardUsed'] = str(cparams.leaderboardUsed)
        context_dict['classSkillsDisplayed'] = str(cparams.classSkillsDisplayed)
        context_dict['virtualCurrencyUsed'] = cparams.virtualCurrencyUsed
       
    # SERIOUS CHALLENGES
    # Get the earned points
    earnedSeriousChallengePoints = 0 

    if not context_dict is None:
        print("context dict is not none")
        chall_name = []
        score = []
        total = []
        challavg = []

    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=True).order_by('challengePosition')
    for challenge in courseChallenges:
        seriousChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)

        if not startOfTime and seriousChallenge.exists():
            seriousChallenge = seriousChallenge.filter(endTimestamp__gte=date_time)

        # Ignore challenges that have invalid total scores
        if seriousChallenge and seriousChallenge[0].challengeID.totalScore < 0:
            continue
        # Get the scores for this challenge then either add the max score
        # or the first score to the earned points variable
        gradeID  = []    
        for serious in seriousChallenge:
            gradeID.append(float(serious.getScoreWithBonus())) # get the score + adjustment + bonus

        if xpSeriousMaxScore and gradeID:                           
            earnedSeriousChallengePoints += max(gradeID)           
        elif gradeID:
            earnedSeriousChallengePoints += float(seriousChallenge.first().getScoreWithBonus())

        # Setup data for rendering this challenge in html (bar graph stuff)
        if not context_dict is None and gradeID:
            chall_name.append(challenge.challengeName)
            challavg.append(classResults.classAverChallengeScore(
                    course, challenge.challengeID))

            if seriousChallenge and gradeID:
                if xpSeriousMaxScore:
                    score.append(max(gradeID))
                else:
                    score.append(gradeID[0])
                # Total possible points for challenge
                total.append(float(seriousChallenge[0].challengeID.getCombinedScore()))
            else:
                score.append(0)
                total.append(0)
    
    # Weighting the total serious challenge points to be used in calculation of the XP Points  
    weightedSeriousChallengePoints = earnedSeriousChallengePoints * xpWeightSChallenge / 100
    print("total score points serious", weightedSeriousChallengePoints)
    
    if not context_dict is None:
        totalPointsSeriousChallenges = sum(total)
        context_dict['challenge_range'] = list(zip(range(1, len(chall_name)+1), chall_name, score, total))
        context_dict['challengeWithAverage_range'] = list(zip(range(1, len(chall_name)+1), chall_name, score, total, challavg))

    # WARMUP CHALLENGES
    # Get the earned points
    earnedWarmupChallengePoints = 0 

    if not context_dict is None:
        chall_Name = []
        total = []
        noOfAttempts = []
        warmUpMaxScore = []
        warmUpMinScore = []
        warmUpSumScore = []
        warmUpSumPossibleScore = []
    
    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in courseChallenges:
        
        warmupChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)

        if not startOfTime and warmupChallenge.exists():
            warmupChallenge = warmupChallenge.filter(endTimestamp__gte=date_time)

        # Ignore challenges that have invalid total scores
        if warmupChallenge and warmupChallenge[0].challengeID.totalScore < 0:
            continue

        # Get the scores for this challenge then either add the max score
        # or the first score to the earned points variable
        gradeID  = []         
        for warmup in warmupChallenge:
            gradeID.append(float(warmup.testScore))   

        if xpWarmupMaxScore and gradeID:                          
            earnedWarmupChallengePoints += max(gradeID)
        elif gradeID:
            earnedWarmupChallengePoints += float(warmupChallenge.first().testScore)

        # Setup data for rendering this challenge in html (bar graph stuff)
        if not context_dict is None and warmupChallenge:
            chall_Name.append(challenge.challengeName)
            # total possible points for challenge
            total.append(warmupChallenge[0].challengeID.totalScore)
            noOfAttempts.append(warmupChallenge.count())
            # Total possible points for all attempts for this challenge
            warmUpSumPossibleScore.append(warmupChallenge[0].challengeID.totalScore*warmupChallenge.count())
            
            if gradeID:
                warmUpMaxScore.append(max(gradeID))
                warmUpMinScore.append(min(gradeID))
                warmUpSumScore.append(sum(gradeID))
            else:
                warmUpMaxScore.append(0)
                warmUpMinScore.append(0)
                warmUpSumScore.append(0)
            
    # Weighting the total warmup challenge points to be used in calculation of the XP Points  
    weightedWarmupChallengePoints = earnedWarmupChallengePoints * xpWeightWChallenge / 100      # max grade for this challenge
    print("points warmup chal xp weighted", weightedWarmupChallengePoints) 

    if not context_dict is None:
        totalWCEarnedPoints = sum(warmUpSumScore)
        totalWCPossiblePoints = sum(warmUpSumPossibleScore)
        context_dict['warmUpContainerHeight'] = 100+60*len(chall_Name)
        context_dict['studentWarmUpChallenges_range'] = list(zip(range(1, len(
            chall_Name)+1), chall_Name, total, noOfAttempts, warmUpMaxScore, warmUpMinScore))
        context_dict['totalWCEarnedPoints'] = totalWCEarnedPoints
        context_dict['totalWCPossiblePoints'] = totalWCPossiblePoints

    # ACTIVITIES
    # Get the earned points
    earnedActivityPoints = 0
    total = []

    courseActivities = Activities.objects.filter(courseID=course)
    for activity in courseActivities:
        studentActivities = StudentActivities.objects.filter(studentID=studentId, courseID=course,activityID=activity)
        if not startOfTime and studentActivities.exists():
            studentActivities = studentActivities.filter(timestamp=date_time)
        
        # Get the scores for this challenge then add the max score
        # to the earned points variable
        gradeID  = []                            
        for studentActivity in studentActivities:
            gradeID.append(float(studentActivity.getScoreWithBonus())) 
                               
        if gradeID:
            earnedActivityPoints += max(gradeID)
        if studentActivities.exists():
             total.append(float(studentActivities[0].activityID.points))

    # Weighting the total activity points to be used in calculation of the XP Points  
    weightedActivityPoints = earnedActivityPoints * xpWeightAPoints / 100
    totalPointsActivities = sum(total)
    print("activity points earned", earnedActivityPoints)
    print("activity points total weighted", weightedActivityPoints)
    print("activity points total", totalPointsActivities)

    # SKILL POINTS
    # Get the earned points
    earnedSkillPoints = 0

    skill_Name = []                
    skill_Points = []
    skill_ClassAvg = []
    
    cskills = CoursesSkills.objects.filter(courseID=course)
    for sk in cskills:
        
        skill = Skills.objects.get(skillID=sk.skillID.skillID)
        skill_Name.append(skill.skillName)
        
        sp = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId,skillID = skill)
        print ("Skill Points Records", sp)
        
        if not sp:  
            skill_Points.append(0)                     
        else:    
            # Get the scores for this challenge then add the max score
            # to the earned points variable               
            gradeID  = []
            
            for p in sp:
                gradeID.append(int(p.skillPoints))
                print("skillPoints", p.skillPoints)   
            
            sumSkillPoints = sum(gradeID,0)                
            earnedSkillPoints += sumSkillPoints

            skill_Points.append(sumSkillPoints)
            skill_ClassAvg.append(classResults.skillClassAvg(
                skill.skillID, course))
    
    if not context_dict is None:
        context_dict['skill_range'] = list(
            zip(range(1, len(skill_Name)+1), skill_Name, skill_Points))
        context_dict['nondefskill_range'] = list(
            zip(range(1, len(skill_Name)+1), skill_Name, skill_Points))
        context_dict['skillWithAverage_range'] = list(
            zip(range(1, len(skill_Name)+1), skill_Name, skill_ClassAvg))


    # Weighting the total skill points to be used in calculation of the XP Points     
    print("earnedSkillPoints: ", earnedSkillPoints)              
    weightedSkillPoints = earnedSkillPoints * xpWeightSP / 100   
    
    # Return the xp and/or required variables rounded to 1 decimal place
    if gradeWarmup:
        xp = round(weightedWarmupChallengePoints,1)
        print("warmup ran")
    elif gradeSerious:
        xp = round(weightedSeriousChallengePoints,1)
        print("serious ran")
    elif seriousPlusActivity:
        xp = round((weightedSeriousChallengePoints  + weightedActivityPoints),1)
        print("serious plus activity ran")
    else:
        xp = round((weightedSeriousChallengePoints + weightedWarmupChallengePoints  + weightedActivityPoints + weightedSkillPoints),1)
        print("xp has ran")
    
    if not context_dict is None:
        return context_dict , xp, weightedSeriousChallengePoints, weightedWarmupChallengePoints, weightedActivityPoints, weightedSkillPoints, earnedSeriousChallengePoints, earnedWarmupChallengePoints, earnedActivityPoints, earnedSkillPoints, totalPointsSeriousChallenges, totalPointsActivities
    
    return (studentId,xp)

def get_or_create_schedule(minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*', tz=settings.TIME_ZONE):
    ''' This will get the crontab schedule if it exists and if not it will create it and return it '''
    from django.conf import settings

    if settings.CURRENTLY_MIGRATING:
        return None
        
    schedules = CrontabSchedule.objects.filter(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year, timezone=tz)
    if schedules.exists():
        if len(schedules) > 1:
            schedule_keep = schedules.first()
            CrontabSchedule.objects.exclude(pk__in=schedule_keep).delete()
            return schedule_keep
        else:
            return schedules.first()
    else:
        schedule = CrontabSchedule.objects.create(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year, timezone=tz)
        return schedule

class TimePeriods:
    ''' TimePeriods enum starting at 1500.
        schedule: crontab of when to run
        datetime: used for results only to look back a time period
        frequency: rate at which to run the task. ex. frequency 2 (daily) will run every other day
    '''
    daily = 1500 # Runs every day at midnight
    weekly = 1501 # Runs every Sunday at midnight
    biweekly = 1502 # Runs every two weeks on Sunday at midnight
    beginning_of_time = 1503 # Runs only once
    daily_test = 1599
    minute_test = 1598
    timePeriods = {
        daily:{
            'index': daily,
            'name': 'daily',
            'displayName': 'Daily at Midnight',
            'schedule': get_or_create_schedule(
                        minute='59', hour='23', day_of_week='*', 
                        day_of_month='*', month_of_year='*'),
            'datetime': lambda: timezone.now() - timedelta(days=1),
            'frequency': 1,
        },
        weekly:{
            'index': weekly,
            'name': 'weekly',
            'displayName': 'Weekly on Sundays at Midnight',
            'schedule': get_or_create_schedule(minute="59", hour="23", day_of_week='0'),
            'datetime': lambda: timezone.now() - timedelta(days=7),
            'frequency': 1,
        },
        biweekly:{
            'index': biweekly,
            'name': 'biweekly',
            'displayName': 'Every Two Weeks on Sundays at Midnight',
            'schedule': get_or_create_schedule(minute="59", hour="23", day_of_week='0'),
            'datetime': lambda: timezone.now() - timedelta(days=14),
            'frequency': 2,
        },
        beginning_of_time:{
            'index': beginning_of_time,
            'name': 'beginning_of_time',
            'displayName': 'Only once at Midnight',
            'schedule': get_or_create_schedule(minute="59", hour="23"),
            'datetime': lambda: None,
            'frequency': 1,
        }
    }
    if __debug__:
        timePeriods[daily_test] = {
            'index': daily_test,
            'name': 'daily_test',
            'displayName': 'Every other Day (For Testing)',
            'schedule': get_or_create_schedule(
                        minute='59', hour='23', day_of_week='*', 
                        day_of_month='*', month_of_year='*'),
            'datetime': lambda: timezone.now() - timedelta(days=2),
            'frequency': 2,
        }
        timePeriods[minute_test] = {
            'index': minute_test,
            'name': 'minute_test',
            'displayName': 'Every other Minute (For Testing)',
            'schedule': get_or_create_schedule(
                        minute='*/2'),
            'datetime': lambda: timezone.now() - timedelta(minutes=2),
            'frequency': 1,
        }
class PeriodicVariables:
    '''PeriodicVariables enum starting at 1400.'''
    
    highest_earner = 1400
    student_warmup_practice = 1401
    unique_warmups = 1402
    xp_ranking = 1403
    warmup_challenges = 1404
    serious_challenge = 1405
    serious_challenges_and_activities = 1406
    attendance_streak = 1407
    challenge_streak = 1408
    warmup_challenge_greater_or_equal_to_40 = 1409
    warmup_challenge_greater_or_equal_to_70 = 1410
    number_of_days_of_unique_warmups_90 = 1411
    number_of_days_of_unique_warmups_70 = 1412
    warmup_challenge_greater_or_equal_to_40_by_day = 1413
    warmup_challenge_greater_or_equal_to_70_by_day = 1414

    
    periodicVariables = {
        highest_earner: {
            'index': highest_earner,
            'name': 'highest_earner',
            'displayName': 'Highest Virtual Currency Earner',
            'description': 'Calculates the highest earner(s) of students based on the virtual currency they have earned',
            'function': calculate_student_earnings,
        },
        student_warmup_practice: {
            'index': student_warmup_practice,
            'name': 'student_warmup_practice',
            'displayName': 'Number of Warmup Challenges Practiced',
            'description': 'The total amount a student has completed any warmup challenges. Including multiple attempts',
            'function': calculate_student_warmup_practice,
        },
        unique_warmups: {
            'index': unique_warmups,
            'name': 'unique_warmups',
            'displayName': 'Warmup Challenges Score (greater than 70% correct)',
            'description': 'The number of unique warmup challenges a student has completed with a score greater than 70%. The student score only includes the student challenge score, adjustment, and curve.',
            'function': calculate_unique_warmups,
        },
        xp_ranking: {
            'index': xp_ranking,
            'name': 'xp_ranking',
            'displayName': 'Student Rankings via XP',
            'description': 'Retrieves the XP for all students in a class',
            'function': calculate_student_xp_rankings,
        },
        warmup_challenges: {
            'index': warmup_challenges,
            'name': 'warmup_challenges',
            'displayName': 'Student Rankings via Warmup Challenges',
            'description': 'Retrieves the warmup challenges points for all students in a class',
            'function': calculate_warmup_rankings,
        },
        serious_challenge: {
            'index': serious_challenge,
            'name': 'serious_challenge',
            'displayName': 'Student Rankings via Serious Challenges',
            'description': 'Retrieves the serious challenges points for all students in a class',
            'function': calculate_serious_challenge_rankings,
        },
        serious_challenges_and_activities: {
            'index': serious_challenges_and_activities,
            'name': 'serious_challenges_and_activities',
            'displayName': 'Student Rankings via Serious Challenges and Activities',
            'description': 'Retrieves the serious challenges and activities points for all students in a class',
            'function': calculate_serious_challenge_and_activity_rankings,
        },
        attendance_streak: {
            'index': attendance_streak,
            'name': 'attendance_streak',
            'displayName': 'Student Attendance Streak',
            'description': 'Retrieves the student attendance streak of the number of days marked as present',
            'function': calculate_student_attendance_streak,
        },
        warmup_challenge_greater_or_equal_to_40: {
            'index': warmup_challenge_greater_or_equal_to_40,
            'name': 'warmup_challenge_gte_40',
            'displayName': 'Warmup Challenge Streak Score >= 40%',
            'description': 'The student Warmup Challenge Streak Score that is greater than or equal to 40%',
            'function': calculate_warmup_challenge_greater_or_equal_to_40,
        },
        warmup_challenge_greater_or_equal_to_70: {
            'index': warmup_challenge_greater_or_equal_to_70,
            'name': 'warmup_challenge_gte_70',
            'displayName': 'Warmup Challenge Streak Score >= 70%',
            'description': 'The student Warmup Challenge Streak Score that is greater than or equal to 70%',
            'function': calculate_warmup_challenge_greater_or_equal_to_70,
        },
        warmup_challenge_greater_or_equal_to_70_by_day: {
            'index': warmup_challenge_greater_or_equal_to_70_by_day,
            'name': 'warmup_challenge_gte_70_by_day',
            'displayName': 'Warmup Challenge Streak Score >= 70% over a period of time',
            'description': 'The student Warmup Challenge Streak Score that is greater than or equal to 70% over a period of time',
            'function': calculate_warmup_challenge_greater_or_equal_to_70_by_day,
        },
        warmup_challenge_greater_or_equal_to_40_by_day: {
            'index': warmup_challenge_greater_or_equal_to_40_by_day,
            'name': 'warmup_challenge_gte_40_by_day',
            'displayName': 'Warmup Challenge Streak Score >= 40% over a period of time',
            'description': 'The student Warmup Challenge Streak Score that is greater than or equal to 40% over a period of time',
            'function': calculate_warmup_challenge_greater_or_equal_to_40_by_day,
        },
        challenge_streak: {
            'index': challenge_streak,
            'name': 'challenge_streak',
            'displayName': 'Challenge Streak',
            'description': 'The number of challenges a student has completed while the student has a streak',
            'function': calculate_student_challenge_streak,
        },
        number_of_days_of_unique_warmups_90: {
            'index': number_of_days_of_unique_warmups_90,
            'name': 'number_of_days_of_unique_warmups_90',
            'displayName': 'Number Of Days Of Unique Warmup Challenges Score > 90%',
            'description': 'The number of days of unique warmup challenges students completed with a score greater than 90%. The student scores only includes the student score, adjustment, and curve.',
            'function': calculate_number_of_days_of_unique_warmups_greater_than_90,
        },
        number_of_days_of_unique_warmups_70: {
            'index': number_of_days_of_unique_warmups_70,
            'name': 'number_of_days_of_unique_warmups_70',
            'displayName': 'Number Of Days Of Unique Warmup Challenges Score > 70%',
            'description': 'The number of days of unique warmup challenges students completed with a score greater than 70%. The student scores only includes the student score, adjustment, and curve.',
            'function': calculate_number_of_days_of_unique_warmups_greater_than_70,
        },
    }

if __debug__:
    # Check for mistakes in the periodicVariables enum, such as duplicate id numbers
    periodic_variable_fields = ['index','name','displayName','description','function']
    
    periodic_variable_names = [pv for pv in PeriodicVariables.__dict__ if pv[:1] != '_' and pv != 'periodicVariables']
    periodic_variable_set = set()
    for periodic_variable_name in periodic_variable_names:
        periodic_variable_number = PeriodicVariables.__dict__[periodic_variable_name]
        periodic_variable_set.add(periodic_variable_number)
        
        assert periodic_variable_number in PeriodicVariables.periodicVariables, "Periodic variable number created without corresponding structure in periodicVariables dictionary.  %s = %i " % (periodic_variable_name, periodic_variable_number)
       
        dictEntry = PeriodicVariables.periodicVariables[periodic_variable_number]
        
        for field in periodic_variable_fields:
            assert field in dictEntry, "Periodic variable structure missing expected field.  %s missing %s" % (periodic_variable_name,field)
        
        assert ' ' not in dictEntry['name'], "Periodic variable structure name field must not have spaces.  (%s)" % (periodic_variable_name)

        assert periodic_variable_number == dictEntry['index'], "Periodic variable structure index field must match periodic variable number. %s -> %i != %i" % (periodic_variable_name, periodic_variable_number, dictEntry['index'])

    assert len(periodic_variable_names) == len(periodic_variable_set), "Two periodic variables have the same number."
