from django_celery_beat.models import CrontabSchedule, PeriodicTask, PeriodicTasks
from Badges.tasks import app
from django.utils import timezone
from datetime import timedelta
import json
import random
import logging
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
        The timeperiod is used for how many days/minutes to go back from now.
        Ex. Time Period: Weekly - Return results within 7 days ago
        
        Returns list of tuples: [(student, value), (student, value),...]
    '''
    from Students.models import StudentRegisteredCourses
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    time_period = TimePeriods.timePeriods[period_index]
    # Get the course object and periodic variable
    course = get_course(course_id)
    # Get all the students in this course
    students = StudentRegisteredCourses.objects.filter(courseID=course)
    rank = []
    # Evaluate each student based on periodic variable function
    for student_in_course in students:
        rank.append(periodic_variable['function'](course, student_in_course.studentID, periodic_variable, time_period, result_only=True))
    
    return rank

def delete_periodic_task(unique_id, variable_index, award_type, course):
    ''' Deletes Periodic Task when rule or badge is deleted'''

    if award_type != "badge" and award_type != "vc" and award_type != "leaderboard":
        logger.error("Cannot delete Periodic Task Object: award_type is not 'badge' or 'vc'!!")

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
        Both can be provied to give both to student(s).

        Note: unique_id is either PeriodicBadgeID(badgeID) or VirtualCurrencyPeriodicRuleID(vcRuleID)
        Note: operator_type is string and is_random is a boolean. Everything else should be an integer
        None: if number_of_top_students and is_random is null then all is assumed (see number 4)
    '''
    from Students.models import StudentRegisteredCourses, PeriodicallyUpdatedleaderboards

    # Get the periodic variable and time period
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    time_period = TimePeriods.timePeriods[period_index]

    # Get the course
    course = get_course(course_id)

    # Set the award type used for finding Periodic Task object
    award_type = ""
    if badge_id:
        award_type += "badge"
    if virtual_currency_amount:
        award_type += "vc"
    if is_leaderboard:
        award_type += "leaderboard"

    unique_str = str(unique_id)+"_"+award_type
    # Aquire the lock for the task 
    lock_id = "lock-{}".format(periodic_variable['name']+'_'+unique_str)
    with memcache_lock(lock_id, app.oid) as acquired:
        if not acquired:
            return
    
    periodic_task = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id))
    total_runs = periodic_task.total_run_count
    print("TOTAL RUNS {}".format(total_runs))
    # Handle beginning of time period
    if time_period == TimePeriods.timePeriods[TimePeriods.beginning_of_time]:
        # If it has ran once then return and set it not to run anymore
        if total_runs >= 1:
            periodic_task.enabled = False
            periodic_task.save()
            return
    # Check for frequency to see handle every N days/month/week etc
    # ex. biweekly
    # (day 1) total_runs = 0 , frequency = 2, task will run
    # (day 7) total_runs = 1 , frequency = 2, task will not run
    # (day 14) total_runs = 2 , frequency = 2, task will run
    # ...
    
    if total_runs % time_period['frequency'] != 0:
        periodic_task.total_run_count += 1
        periodic_task.save()
        return

    # Handle beginning of time period
    if time_period == TimePeriods.timePeriods[TimePeriods.beginning_of_time]:
        unique_str = str(unique_id)+"_"+award_type
        periodic_task = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id))
        total_runs = periodic_task.total_run_count
        if total_runs >= 1:
            periodic_task.enabled = False
            periodic_task.save()
            return

    # Get all the students in this course, exclude test student
    students = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)
    rank = []
    # Evaluate each student based on periodic variable function
    for student_in_course in students:
        rank.append(periodic_variable['function'](course, student_in_course.studentID, periodic_variable, time_period, unique_id=unique_id, award_type=award_type))


    print("Results: {}".format(rank))
    # Filter out students based on periodic badge/vc rule settings
    if not is_leaderboard and not save_results:
        rank = filter_students(rank, number_of_top_students, threshold, operator_type, is_random)
        print("Filtered: {}".format(rank))
        # Give award to students
        award_students(rank, course, badge_id, virtual_currency_amount)
    elif save_results:
        if is_leaderboard:
            # Sort the students
            rank.sort(key=lambda tup: tup[1], reverse=True)
            # Check if what we want is greater than the number of students
            if len(rank) >= number_of_top_students+1:
                # Only select the top number of students
                rank = rank[:number_of_top_students+1]
                
                # save results (leaderboard_id == unique_id)
                savePeriodicLeaderboardResults(rank,unique_id, course)
            else:
                savePeriodicLeaderboardResults(rank,unique_id, course)
    periodic_task.total_run_count += 1
    periodic_task.save()

def filter_students(students, number_of_top_students, threshold, operator_type, is_random):
    ''' Filters out students based on parameters if they are not None.
        number_of_top_students: gets the top number of students wanted
        threshold & operator_type: gets the students which are above/at a threshold
        is_random: randomly chooses a student. Can be paired with threshold.
    '''

    if students:
        operatorType = {
            '>=': lambda x, y : x >= y,
            '>' : lambda x, y : x > y,
            '=' : lambda x, y : x == y
        }
        # Filter students based on if their result passes the threshold
        students = [(student, val) for student, val in students if operatorType[operator_type](val, threshold)]

        if number_of_top_students and students:
            # Sort the students
            students.sort(key=lambda tup: tup[1])
            # Check if what we want is greater than the number of students
            if len(students) >= number_of_top_students:
                # Only select the top number of students
                students = students[:number_of_top_students]
        elif is_random and students:
            # If random, choose one student and remove everyone else
            random.shuffle(students)
            students = random.sample(students, 1)
    return students
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

        
    
def award_students(students, course, badge_id=None, virtual_currency_amount=None):
    ''' Awards students a badge or virtual currency or both.'''

    from notify.signals import notify  
    from Students.models import StudentBadges, StudentRegisteredCourses
    from Badges.models import BadgesInfo
    from Instructors.views.utils import utcDate

    for student, result in students:
        # Give award for either badge or virtual currency
        if badge_id:
            # Check if student has earned this badge
            studentBadges = StudentBadges.objects.filter(studentID = student, badgeID = badge_id)
            if studentBadges.exists():
                logger.debug("Badge already earned")
                return

            # If the badge has not already been earned, then award it 
            badge = BadgesInfo.objects.get(pk=badge_id)
   
            studentBadge = StudentBadges()
            studentBadge.studentID = student
            studentBadge.badgeID = badge
            studentBadge.objectID = 0
            studentBadge.timestamp = utcDate()
            studentBadge.save()
            
            # Notify student of badge award 
            notify.send(None, recipient=student.user, actor=student.user, verb='You won the '+badge.badgeName+' badge', nf_type='Badge', extra=json.dumps({"course": str(course.courseID)}))
            
        # Give award of virtual currency
        if virtual_currency_amount:
            if virtual_currency_amount > 0:
                student_profile = StudentRegisteredCourses.objects.get(courseID=course, studentID=student)
                student_profile.virtualCurrencyAmount += virtual_currency_amount
                student_profile.save()
                # Notify student of VC award 
                notify.send(None, recipient=student.user, actor=student.user, verb='You won '+str(virtual_currency_amount)+' course bucks', nf_type='Increase VirtualCurrency', extra=json.dumps({"course": str(course.courseID)}))

def get_last_ran(unique_id, variable_index, award_type, course_id):
    ''' Retrieves the last time a periodic task has ran. 
        Returns None if it is has not ran yet.
    '''
    # print("award type", award_type)
    if not "badge" in award_type  and not "vc" in award_type and not "leaderboard" in award_type:
        logger.error("Cannot find Periodic Task Object: award_type is not 'badge' or 'vc' or 'leaderboard'!!")

    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    unique_str = str(unique_id)+"_"+award_type

    last_ran = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id)).last_run_at
    return last_ran
def set_last_ran(unique_id, variable_index, award_type, course_id):
    ''' Sets periodic task last time ran datefield. It is not updated accurately by itself.'''
    from Instructors.views.utils import utcDate
    if not "badge" in award_type  and not "vc" in award_type and not "leaderboard" in award_type:
        logger.error("Cannot find Periodic Task Object: award_type is not 'badge' or 'vc' or 'leaderboard'!!")

    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    unique_str = str(unique_id)+"_"+award_type

    task = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id))
    task.last_run_at = utcDate()
    task.save()
    PeriodicTasks.changed(task)

def calculate_student_earnings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    ''' This calculates the student earnings of virtual currency since the last period.
        Earnings are defined by only what virtual currency they gained and not spent.'''
    
    print("Calculating Highest Earner") 
    from Students.models import StudentVirtualCurrency
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule, LeaderboardsConfig

    # print("result only", result_only)
    # Get the last time this periodic variable has ran if not getting results only (leaderboards)
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    else:
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
    # print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(total))

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, total)

def calculate_student_warmup_practice(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
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

    last_ran = None
    # Get the last time this periodic variable has ran
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)    
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
                
                p = date_time()
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

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, practices)

def calculate_unique_warmups(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    ''' This calculates the number of unique Warm-up challenges the student has completed
        with a score greater than 70%.
    '''
    print("Calculating Unique Warmups with a Score > 70%") 
    from Instructors.models import Challenges
    from Students.models import StudentChallenges
    from decimal import Decimal
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    last_ran = None
    # Get the last time this periodic variable has ran
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)    
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
            # Say this challenge is counted for if the student score percentage is greater than 80%
            if percentage > Decimal(70.0):
                unique_warmups += 1

    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Unique Warm-ups: {}".format(unique_warmups))

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, unique_warmups)
def calculate_student_attendance_streak(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    print("Calculating student_attendance_streak") 
    #this one is best ran with daily time period
    #weekly will work but cause it to ignore the extra attendance days unless set up properly.
    #should be set before the start of a week, week defined as 7 days. 
    from Students.models import StudentStreaks, StudentAttendance
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule, CourseConfigParams
    from Instructors.models import AttendanceStreakConfiguration
    from datetime import datetime, timedelta
    import ast
    
    # Get the last time this periodic variable has ran if not getting results only (leaderboards)
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    else:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None
            
    treshold = 0
    resetStreak = False
    
    #if detemine which type of award this is and obtain tresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            treshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            treshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
     
    if StudentStreaks.objects.filter(courseID=course.courseID, studentID=student, streakType=0).exists():
        studentStreak = StudentStreaks.objects.filter(courseID=course.courseID, studentID=student)[0]
    else:
        studentStreak = StudentStreaks()
        studentStreak.studentID = student
        studentStreak.courseID = course
        studentStreak.streakStartDate = datetime.now().strftime("%Y-%m-%d")
        studentStreak.streakType = 0
        studentStreak.objectID = unique_id
        studentStreak.currentStudentStreakLength = 0      
        
    
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
            
    total = 0
    #determine what to do with their attendance
    if isTodayStreakDay:
        
        if StudentAttendance.objects.filter(courseID=course.courseID, studentID=student, timestamp=datetime.now().strftime("%Y-%m-%d")).exists():
            studentStreak.currentStudentStreakLength += 1
            total = studentStreak.currentStudentStreakLength
            
            #if total is larger than streak and we want to NOT reset streak
            if total > treshold and resetStreak:
                studentStreak.currentStudentStreakLength = 0
                total = treshold
            elif total > treshold and not resetStreak:
                if total % treshold == 0:
                    total = treshold
                else:
                    #total is set as remainder of current streak length and treshold
                    total %= treshold
            elif total == treshold and resetStreak:
                studentStreak.currentStudentStreakLength = 0
                total = treshold
            elif total == treshold and not resetStreak:
                total = treshold
                
        else:
            studentStreak.currentStudentStreakLength = 0
            total = 0
                        
    studentStreak.save()
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(total))

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, total)

def calculate_student_xp_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id, result_only,  gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False)
    
def calculate_warmup_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id, result_only, gradeWarmup=True, gradeSerious=False, seriousPlusActivity=False)
    
def calculate_serious_challenge_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id,result_only, gradeWarmup=False, gradeSerious=True, seriousPlusActivity=False)
    
def calculate_serious_challenge_and_activity_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentScore(student, course, periodic_variable, time_period, unique_id ,result_only, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=True)

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, total)
def calculate_student_challenge_streak(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    print("Calculating student challenge streak") 
    from Students.models import StudentStreaks, StudentChallenges
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    from datetime import datetime
    # Get the last time this periodic variable has ran if not getting results only (leaderboards)
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    else:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None
           
    treshold = 0
    resetStreak = False  
    #if detemine which type of award this is and obtain tresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            treshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            treshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
     
    if StudentStreaks.objects.filter(courseID=course.courseID, studentID=student, streakType=0).exists():
        studentStreak = StudentStreaks.objects.filter(courseID=course.courseID, studentID=student)[0]
    else:
        studentStreak = StudentStreaks()
        studentStreak.studentID = student
        studentStreak.courseID = course
        studentStreak.streakStartDate = datetime.now()
        studentStreak.streakType = 0
        studentStreak.objectID = unique_id
        studentStreak.currentStudentStreakLength = 0   
        
    total = 0
    
    #figure out how many challenges have been completed by the student
    challengeCount = len(StudentChallenges.objects.filter(studentID=student, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d"))))
    studentStreak.currentStudentStreakLength += challengeCount
    
    total = studentStreak.currentStudentStreakLength
    #if total is larger than streak and we want to NOT reset streak
    if total > treshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        total = treshold
    elif total > treshold and not resetStreak:
        if total % treshold == 0:
            total = treshold
        else:
            #total is set as remainder of current streak length and treshold
            total %= treshold
    elif total == treshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        total = treshold
    elif total == treshold and not resetStreak:
        total = treshold
        
    studentStreak.save()
    
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(total))

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, total)
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
def calculate_student_challenge_streak_for_percentage(percentage, course, student, periodic_variable, time_period, unique_id, award_type, result_only):
    print("Calculating student challenge >= streak") 
    from Students.models import StudentStreaks, StudentChallenges
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule
    from datetime import datetime
    from Instructors.models import Challenges

    percentage = percentage *.01
        # Get the last time this periodic variable has ran
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)    
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
        elif result_only:
            date_time = time_period['datetime']
            if date_time:
                last_ran = date_time()
            else:
                last_ran = None
    # Get the last time this periodic variable has ran if not getting results only (leaderboards)
    if not result_only:
        last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    else:
        date_time = time_period['datetime']
        if date_time:
            last_ran = date_time()
        else:
            last_ran = None
           
    treshold = 0
    resetStreak = False  
    #if detemine which type of award this is and obtain tresholds and resetStreak booleans
    if award_type == 'badge':
        if PeriodicBadges.objects.filter(badgeID=unique_id).exists():
            periodicBadge = PeriodicBadges.objects.filter(badgeID=unique_id)[0]
            treshold = periodicBadge.threshold
            resetStreak = periodicBadge.resetStreak
    elif award_type == 'vc':
        if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id).exists():
            periodicVC = VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=unique_id)[0]
            treshold = periodicVC.threshold
            resetStreak = periodicVC.resetStreak
     
    if StudentStreaks.objects.filter(courseID=course.courseID, studentID=student, streakType=0).exists():
        studentStreak = StudentStreaks.objects.filter(courseID=course.courseID, studentID=student)[0]
    else:
        studentStreak = StudentStreaks()
        studentStreak.studentID = student
        studentStreak.courseID = course
        studentStreak.streakStartDate = datetime.now()
        studentStreak.streakType = 0
        studentStreak.objectID = unique_id
        studentStreak.currentStudentStreakLength = 0   
        
    total = 0
    
    #figure out how many challenges have been completed by the student
    challengeCount = len(StudentChallenges.objects.filter(studentID=student, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d"))))
    studentChallengeIDs = []
    maxScores = []

    if challengeCount > 1:
        studentChallenges = StudentChallenges.objects.filter(studentID=student, courseID=course.courseID, endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d")))
        for challenge in studentChallenges:
            studentChallengeIDs.append(challenge.challengeID)
        challengeScores = []
        for studentChallengeID in studentChallengeIDs:
            if getPercentageScoreForStudent(studentChallengeID, student, percentage, last_ran):
                total += 1
    elif challengeCount == 1:
        print("challCount==1")
        studentChallenge = StudentChallenges.objects.filter(studentID=student, courseID=course.courseID,
        endTimestamp__range=(datetime.now().strftime("%Y-%m-%d"), last_ran.strftime("%Y-%m-%d")))[0]
        challenge = Challenges.objects.filter(challengeID=studentChallenge.challengeID)[0]
        if (studentChallenge.testScore/challenge.challengeTotalScore) >= (percentage):
            total += 1
        
    #if total is larger than streak and we want to NOT reset streak
    if total > treshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        total = treshold
    elif total > treshold and not resetStreak:
        if total % treshold == 0:
            total = treshold
        else:
            #total is set as remainder of current streak length and treshold
            total %= treshold
    elif total == treshold and resetStreak:
        studentStreak.currentStudentStreakLength = 0
        total = treshold
    elif total == treshold and not resetStreak:
        total = treshold
        
    studentStreak.save()
    
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(total))

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, total)
def calculate_warmup_challenge_greater_or_equal_to_70(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return calculate_student_challenge_streak_for_percentage(70,course, student, periodic_variable, time_period, unique_id, award_type, result_only)
def calculate_warmup_challenge_greater_or_equal_to_40(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return calculate_student_challenge_streak_for_percentage(40,course, student, periodic_variable, time_period, unique_id, award_type, result_only)
def get_or_create_schedule(minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'):
    from django.conf import settings
    if settings.CURRENTLY_MIGRATING:
        return None
    schedules = CrontabSchedule.objects.filter(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year)
    if schedules.exists():
        if len(schedules) > 1:
            schedule_keep = schedules.first()
            CrontabSchedule.objects.exclude(pk__in=schedule_keep).delete()
            return schedule_keep
        else:
            return schedules.first()
    else:
        schedule = CrontabSchedule.objects.create(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year)
        return schedule
                
def studentScore(studentId, course, periodic_variable, time_period, unique_id, result_only=False,gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, context_dict = None):
    
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
        date_time = get_last_ran(unique_id, periodic_variable['index'], "leaderboard", course.courseID) 
        
        if not date_time:
            periodic_leaderboard =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course.courseID)
            backwardsTime = periodic_leaderboard.howFarBack
            
            if backwardsTime == 1500:
                date_time = date.today() - timedelta(1)
                
            elif backwardsTime == 1501:
                date_time = date.today() - timedelta(7)
                
            else:
                date_time = None
            
        set_last_ran(unique_id, periodic_variable['index'], "leaderboard", course.courseID)
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

    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=True)
    for challenge in courseChallenges:
        seriousChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)

        if not startOfTime and seriousChallenge.exists():
            seriousChallenge = seriousChallenge.filter(endTimestamp__gte=date_time)

        # Get the scores for this challenge then either add the max score
        # or the first score to the earned points variable
        gradeID  = []    
        if xpSeriousMaxScore:                           
            for serious in seriousChallenge:
                gradeID.append(int(serious.getScoreWithBonus()))   # get the score + adjustment + bonus
            if gradeID:
                earnedSeriousChallengePoints += max(gradeID)           
        elif seriousChallenge.exists():
            gradeID.append(int(seriousChallenge.first().getScoreWithBonus())) 
            if gradeID:
                earnedSeriousChallengePoints += gradeID[0]

        # Setup data for rendering this challenge in html (bar graph stuff)
        if not context_dict is None:
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
        context_dict['challenge_range'] = list(zip(range(1, len(courseChallenges)+1), chall_name, score, total))
        context_dict['challengeWithAverage_range'] = list(zip(range(1, len(courseChallenges)+1), chall_name, score, total, challavg))

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

        # Get the scores for this challenge then either add the max score
        # or the first score to the earned points variable
        gradeID  = []           
        if xpWarmupMaxScore:                          
            for warmup in warmupChallenge:
                gradeID.append(int(warmup.testScore)) 
            if gradeID:
                earnedWarmupChallengePoints += max(gradeID)
        elif warmupChallenge.exists():
            gradeID.append(int(warmupChallenge.first().testScore))
            if gradeID:
                earnedWarmupChallengePoints += gradeID[0]

        # Setup data for rendering this challenge in html (bar graph stuff)
        if not context_dict is None and warmupChallenge:
            chall_Name.append(challenge.challengeName)
            # total possible points for challenge
            total.append(warmupChallenge[0].challengeID.totalScore)
            noOfAttempts.append(warmupChallenge.count())
            
            if gradeID:
                if xpWarmupMaxScore:
                    warmUpMaxScore.append(max(gradeID))
                    warmUpMinScore.append(min(gradeID))
                    warmUpSumScore.append(sum(gradeID))
                    warmUpSumPossibleScore.append(warmupChallenge[0].challengeID.totalScore*warmupChallenge.count())
                else:
                    warmUpMaxScore.append(warmupChallenge.first().testScore)
                    warmUpMinScore.append(warmupChallenge.first().testScore)
                    warmUpSumScore.append(warmupChallenge.first().testScore)
                    warmUpSumPossibleScore.append(warmupChallenge[0].challengeID.totalScore*warmupChallenge.count())
            else:
                warmUpMaxScore.append(0)
                warmUpMinScore.append(0)
                warmUpSumScore.append(0)
                warmUpSumPossibleScore.append(warmupChallenge[0].challengeID.totalScore*warmupChallenge.count())

            containerHeight = 100
            containerHeight += len(chall_Name) * 60
            
    # Weighting the total warmup challenge points to be used in calculation of the XP Points  
    weightedWarmupChallengePoints = earnedWarmupChallengePoints * xpWeightWChallenge / 100      # max grade for this challenge
    print("points warmup chal xp weighted", weightedWarmupChallengePoints) 

    if not context_dict is None:
        totalWCEarnedPoints = sum(warmUpSumScore)
        totalWCPossiblePoints = sum(warmUpSumPossibleScore)
        context_dict['warmUpContainerHeight'] = containerHeight
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
            gradeID.append(int(studentActivity.getScoreWithBonus())) 
                               
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
    
    # Return the xp and/or required variables
    if gradeWarmup:
        xp = round(weightedWarmupChallengePoints,0)
        print("warmup ran")
    elif gradeSerious:
        xp = round(weightedSeriousChallengePoints,0)
        print("serious ran")
    elif seriousPlusActivity:
        xp = round((weightedSeriousChallengePoints  + weightedActivityPoints),0)
        print("serious plus activity ran")
    else:
        xp = round((weightedSeriousChallengePoints + weightedWarmupChallengePoints  + weightedActivityPoints + weightedSkillPoints),0)
        print("xp has ran")
    
    if not context_dict is None:
        return context_dict , xp, weightedSeriousChallengePoints, weightedWarmupChallengePoints, weightedActivityPoints, weightedSkillPoints, earnedSeriousChallengePoints, earnedWarmupChallengePoints, earnedActivityPoints, earnedSkillPoints, totalPointsSeriousChallenges, totalPointsActivities
    
    return (studentId,xp)

class TimePeriods:
    from django.utils import timezone
    from datetime import timedelta

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
    timePeriods = {
        daily_test:{
            'index': daily_test,
            'name': 'daily_test',
            'displayName': 'Every 2 Minutes (For Testing)',
            'schedule': get_or_create_schedule(
                        minute='*', hour='*', day_of_week='*', 
                        day_of_month='*', month_of_year='*'),
            'datetime': lambda: timezone.now() - timedelta(minutes=2),
            'frequency': 1,
        },
        daily:{
            'index': daily,
            'name': 'daily',
            'displayName': 'Daily at Midnight',
            'schedule': get_or_create_schedule(
                        minute='0', hour='0', day_of_week='*', 
                        day_of_month='*', month_of_year='*'),
            'datetime': lambda: timezone.now() - timedelta(days=1),
            'frequency': 1,
        },
        weekly:{
            'index': weekly,
            'name': 'weekly',
            'displayName': 'Weekly on Sundays at Midnight',
            'schedule': get_or_create_schedule(minute="0", hour="0", day_of_week='0'),
            'datetime': lambda: timezone.now() - timedelta(days=7),
            'frequency': 1,
        },
        biweekly:{
            'index': biweekly,
            'name': 'biweekly',
            'displayName': 'Every Two Weeks on Sundays at Midnight',
            'schedule': get_or_create_schedule(minute="0", hour="0", day_of_week='0'),
            'datetime': lambda: timezone.now() - timedelta(days=14),
            'frequency': 2,
        },
        beginning_of_time:{
            'index': beginning_of_time,
            'name': 'beginning_of_time',
            'displayName': 'Only once at Midnight',
            'schedule': get_or_create_schedule(minute="0", hour="0"),
            'datetime': lambda: None,
            'frequency': 1,
        }
    }
class PeriodicVariables:
    '''PeriodicVariables enum starting at 1400.'''
    
    highest_earner = 1400
    student_warmup_pratice = 1401
    unique_warmups = 1402
    xp_ranking = 1403
    warmup_challenges = 1404
    serious_challenge = 1405
    serious_challenges_and_activities = 1406
    attendance_streak = 1407
    challenge_streak = 1408
    warmup_challenge_greater_or_equal_to_40 = 1409
    warmup_challenge_greater_or_equal_to_70 = 1410
    
    periodicVariables = {
        highest_earner: {
            'index': highest_earner,
            'name': 'highest_earner',
            'displayName': 'Highest Virtual Currency Earner',
            'description': 'Calculates the highest earner(s) of students based on the virtual currency they have earned',
            'function': calculate_student_earnings,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        student_warmup_pratice: {
            'index': student_warmup_pratice,
            'name': 'student_warmup_pratice',
            'displayName': 'Number of Warmup Challenges Practiced',
            'description': 'The amount of times students practiced any warmup challenges',
            'function': calculate_student_warmup_practice,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        unique_warmups: {
            'index': unique_warmups,
            'name': 'unique_warmups',
            'displayName': 'Warmup Challenges Score (greater than 70% correct)',
            'description': 'The number of warmup challenges students completed with a score greater than 70%. The student scores only includes the student score, adjustment, and curve.',
            'function': calculate_unique_warmups,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        xp_ranking: {
            'index': xp_ranking,
            'name': 'xp_ranking',
            'displayName': 'Student Rankings via XP',
            'description': 'Retrieves the Xp for all students in a class',
            'function': calculate_student_xp_rankings,
            'task_type': 'Leaderboard.periodicVariables.periodic_task',
        },
        warmup_challenges: {
            'index': warmup_challenges,
            'name': 'warmup_challenges',
            'displayName': 'Student Rankings via Warmup Challenges',
            'description': 'Retrieves the warmup_challenges and creates a ranking for all students in a class',
            'function': calculate_warmup_rankings,
            'task_type': 'Leaderboard.periodicVariables.periodic_task',
        },
        serious_challenge: {
            'index': serious_challenge,
            'name': 'serious_challenge',
            'displayName': 'Student Rankings via Serious Challenges',
            'description': 'Retrieves the Serious Challenges and creates a ranking for all students in a class',
            'function': calculate_serious_challenge_rankings,
            'task_type': 'Leaderboard.periodicVariables.periodic_task',
        },
        serious_challenges_and_activities: {
            'index': serious_challenges_and_activities,
            'name': 'serious_challenges_and_activities',
            'displayName': 'Student Rankings via Serious Challenges and Activities',
            'description': 'Retrieves the Serious Challenges and Activities and creates a ranking for all students in a class',
            'function': calculate_serious_challenge_and_activity_rankings,
            'task_type': 'Leaderboard.periodicVariables.periodic_task',
        },
        attendance_streak: {
            'index': attendance_streak,
            'name': 'attendance_streak',
            'displayName': 'Student Attendance Streak',
            'description': 'Retrieves the student attendance so far',
            'function': calculate_student_attendance_streak,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        warmup_challenge_greater_or_equal_to_40: {
            'index': warmup_challenge_greater_or_equal_to_40,
            'name': 'Warmup challenge >= 40%',
            'displayName': 'Warmup Challenge Streak Score >= 40%',
            'description': 'Warmup Challenge Streak Score >= 40%',
            'function': calculate_warmup_challenge_greater_or_equal_to_40,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        warmup_challenge_greater_or_equal_to_70: {
            'index': warmup_challenge_greater_or_equal_to_70,
            'name': 'Warmup challenge >= 70%',
            'displayName': 'Warmup Challenge Streak Score >= 70%',
            'description': 'Warmup Challenge Streak Score >= 70%',
            'function': calculate_warmup_challenge_greater_or_equal_to_70,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        
        challenge_streak: {
            'index': challenge_streak,
            'name': 'challenge_streak',
            'displayName': 'Challenge Streak',
            'description': 'Challenge Streak',
            'function': calculate_student_challenge_streak,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
    }

if __debug__:
    # Check for mistakes in the periodicVariables enum, such as duplicate id numbers
    periodic_variable_fields = ['index','name','displayName','description','function','task_type']
    
    periodic_variable_names = [pv for pv in PeriodicVariables.__dict__ if pv[:1] != '_' and pv != 'periodicVariables']
    periodic_variable_set = set()
    for periodic_variable_name in periodic_variable_names:
        periodic_variable_number = PeriodicVariables.__dict__[periodic_variable_name]
        periodic_variable_set.add(periodic_variable_number)
        
        assert periodic_variable_number in PeriodicVariables.periodicVariables, "Periodic variable number created without corresponding structure in periodicVariables dictionary.  %s = %i " % (periodic_variable_name, periodic_variable_number)
       
        dictEntry = PeriodicVariables.periodicVariables[periodic_variable_number]
        for field in periodic_variable_fields:
            assert field in dictEntry, "Periodic variable structure missing expected field.  %s missing %s" % (periodic_variable_name,field)

        assert periodic_variable_number == dictEntry['index'], "Periodic variable structure index field must match periodic variable number. %s -> %i != %i" % (periodic_variable_name, periodic_variable_number, dictEntry['index'])

    assert len(periodic_variable_names) == len(periodic_variable_set), "Two periodic variables have the same number."
