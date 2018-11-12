from django_celery_beat.models import CrontabSchedule, PeriodicTask, PeriodicTasks
from Badges.tasks import app
import json
import random
import logging
logger = logging.getLogger(__name__)

from django.conf import settings

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
    
    # Set the award type used for finding Periodic Task object
    award_type = ""
    if badge_id:
        award_type += "badge"
    if virtual_currency_amount:
        award_type += "vc"
    if is_leaderboard:
        award_type += "leaderboard"

    # Handle beginning of time period
    if time_period == TimePeriods.timePeriods[TimePeriods.beginning_of_time]:
        unique_str = str(unique_id)+"_"+award_type
        periodic_task = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id))
        total_runs = periodic_task.total_run_count
        if total_runs >= 1:
            periodic_task.enabled = False
            periodic_task.save()
            return

    # Get the course
    course = get_course(course_id)

    # Handle beginning of time period
    if time_period == TimePeriods.timePeriods[TimePeriods.beginning_of_time]:
        unique_str = str(unique_id)+"_"+award_type
        periodic_task = PeriodicTask.objects.get(name=periodic_variable['name']+'_'+unique_str, kwargs__contains='"course_id": '+str(course_id))
        total_runs = periodic_task.total_run_count
        if total_runs >= 1:
            periodic_task.enabled = False
            periodic_task.save()
            return

    # Get the course
    course = get_course(course_id)

    # Get all the students in this course, exclude test student
    students = StudentRegisteredCourses.objects.filter(courseID=course)
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
            if len(rank) >= number_of_top_students:
                # Only select the top number of students
                rank = rank[:number_of_top_students]
                
                # save results (leaderboard_id == unique_id)
                savePeriodicLeaderboardResults(rank,unique_id, course)
            else:
                savePeriodicLeaderboardResults(rank,unique_id, course)

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
    print("saving results", rank, leaderboardConfigID, course)
    from Students.models import PeriodicallyUpdatedleaderboards
    from Badges.models import LeaderboardsConfig
  
    leaderboardConfigID = LeaderboardsConfig.objects.get(leaderboardID=int(leaderboardConfigID))
    print("leaderboardConfigID", leaderboardConfigID)
    print("rank", rank)
   
    #we must filter out the test student
    studentsPlusScores = []
    for student in rank:
        if not student[0].isTestStudent:
            studentsPlusScores.append(student)
    index = 1
    
    #iterate over the list of studentsplusscores and make the records or update existing records
    for student in studentsPlusScores:
        print("currentStudent", student,"index" ,index)
        leaderboardRecord = PeriodicallyUpdatedleaderboards.objects.filter(leaderboardID=int(leaderboardConfigID.leaderboardID), studentID=student[0])
        print("leaderboard", leaderboardRecord)
        
        if leaderboardRecord:
            print("we have a record so we should update", leaderboardRecord[0])
            leaderboard = leaderboardRecord[0]
            leaderboard.studentID = student[0]
            leaderboard.studentPoints = student[1]
            leaderboard.studentPosition = index
        else:
            print("creating a new one since we dont have a record for", student)
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
            print("setting -1 to records after our index, no student can be -1")
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
            notify.send(None, recipient=student.user, actor=student.user, verb='You won the '+badge.badgeName+' badge', nf_type='Badge')
            
        # Give award of virtual currency
        if virtual_currency_amount:
            if virtual_currency_amount > 0:
                student_profile = StudentRegisteredCourses.objects.get(courseID=course, studentID=student)
                student_profile.virtualCurrencyAmount += virtual_currency_amount
                student_profile.save()
                # Notify student of VC award 
                notify.send(None, recipient=student.user, actor=student.user, verb='You won '+str(virtual_currency_amount)+' virtual bucks', nf_type='Increase VirtualCurrency')

def get_last_ran(unique_id, variable_index, award_type, course_id):
    ''' Retrieves the last time a periodic task has ran. 
        Returns None if it is has not ran yet.
    '''
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
    earnings = StudentVirtualCurrency.objects.filter(studentID = student, vcRuleID__courseID = course)
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
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule

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

    # Set this as the last time this task has ran
    if not result_only:
        set_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID)
    return (student, practices)

def calculate_unique_warmups(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    ''' This calculates the number of unique Warm-up challenges the student has completed
        with a score greater than 60%.
    '''
    print("Calculating Unique Warmups with a Score > 60%") 
    from Instructors.models import Challenges
    from Students.models import StudentChallenges
    from decimal import Decimal
    from Badges.models import PeriodicBadges, VirtualCurrencyPeriodicRule


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
            total_score_possible = challenge.totalScore
            # Get the highest score out of the student attempts for this challenge (Note: test score is Decimal type)
            highest_score = max([warmup.testScore for warmup in studentChallenges])
            # If the total possible score is not set then skip this Warm-up challenge
            if total_score_possible <= 0:
                continue
            # Calculate the percentage
            percentage = (highest_score/total_score_possible) * Decimal(100)
            # Say this challenge is counted for if the student score percentage is greater than 60%
            if percentage > Decimal(60.0):
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

def calculate_student_xp_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentXP(student, course)
    
def calculate_warmup_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentXP(student, course, warmup=True, serious=False, seriousPlusActivity=False)
    
def calculate_serious_challenge_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentXP(student, course, warmup=False, serious=True, seriousPlusActivity=False)
    
def calculate_serious_challenge_and_activity_rankings(course, student, periodic_variable, time_period, unique_id=None, award_type=None, result_only=False):
    return studentXP(student, course, warmup=False, serious=False, seriousPlusActivity=True)

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
    
def last_ran_leaderboard(unique_id, periodic_variable, award_type, course):
    from Badges.models import LeaderboardsConfig
    # If this is first time running, set the last ran to equal to the time the rule/badge was created/modified since we don't want to get all the previous challenges from beginning of time
    last_ran = get_last_ran(unique_id, periodic_variable['index'], award_type, course.courseID) 
    if not last_ran:
            periodic_badge =  LeaderboardsConfig.objects.get(leaderboardID=unique_id, courseID=course)
            last_ran = periodic_badge.lastModified
                
def studentXP(studentId, course, warmup=False, serious=False, seriousPlusActivity=False):
    
    from Badges.models import CourseConfigParams
    from Instructors.models import Challenges, Activities, CoursesSkills, Skills
    from Students.models import StudentChallenges, StudentActivities, StudentCourseSkills
    xp = 0  
    xpWeightSP = 0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    ccparamsList = CourseConfigParams.objects.filter(courseID=course)
    if len(ccparamsList) >0:
        cparams = ccparamsList[0]
        xpWeightSP=cparams.xpWeightSP
        xpWeightSChallenge=cparams.xpWeightSChallenge
        xpWeightWChallenge=cparams.xpWeightWChallenge
        xpWeightAPoints=cparams.xpWeightAPoints
       
    # get the serious challenges for this course
    earnedScorePoints = 0 
    totalScorePoints = 0    
    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=True, isVisible=True)
    
    for challenge in courseChallenges:
        seriousChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)

        gradeID  = []                            
        for serious in seriousChallenge:
            gradeID.append(int(serious.getScoreWithBonus()))   # get the score + adjustment
                                
        if(gradeID):
            earnedScorePoints += max(gradeID)
            totalScorePoints += challenge.totalScore
            
    totalScorePointsSeriousChallenge = earnedScorePoints * xpWeightSChallenge / 100      # max grade for this challenge
    
    # get the warm up challenges for this course
    earnedScorePoints = 0 
    totalScorePoints = 0   
    
    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=False, isVisible=True)
    for challenge in courseChallenges:
        warmupChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)

        gradeID  = []                            
        for warmup in warmupChallenge:
            gradeID.append(int(warmup.testScore)) 
                               
        if(gradeID):
            earnedScorePoints += max(gradeID)
            totalScorePoints += challenge.totalScore
            
    totalScorePointsWarmupChallenge = earnedScorePoints * xpWeightWChallenge / 100      # max grade for this challenge
                        
    # get the activity points for this course
    earnedActivityPoints = 0
    totalActivityPoints = 0

    courseActivities = Activities.objects.filter(courseID=course)
    for activity in courseActivities:

        sa = StudentActivities.objects.filter(studentID=studentId, courseID=course,activityID=activity)

        gradeID  = []                            
        for a in sa:
            gradeID.append(int(a.getScoreWithBonus())) 
                               
        if(gradeID):
            earnedActivityPoints += max(gradeID)
            totalActivityPoints += a.activityID.points
            
    totalScorePointsActivityPoints = earnedActivityPoints * xpWeightAPoints / 100
            
    # get the skill points for this course
    totalScoreSkillPoints = 0
    cskills = CoursesSkills.objects.filter(courseID=course)
    for sk in cskills:
        skill = Skills.objects.get(skillID=sk.skillID.skillID)
        
        sp = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId,skillID = skill)
        #print ("Skill Points Records", sp)
        gradeID = []
        
        for p in sp:
            gradeID.append(int(p.skillPoints))
            #print("skillPoints", p.skillPoints)
        if (gradeID):
            totalScoreSkillPoints = ((totalScoreSkillPoints + sum(gradeID,0)) * xpWeightSP / 100)
    
    
    if warmup==True:
        xp = round(totalScorePointsWarmupChallenge,0)
    elif serious == True:
        xp = round(totalScorePointsSeriousChallenge,0)
    elif seriousPlusActivity == True:
        xp = round((totalScorePointsSeriousChallenge  + totalScorePointsActivityPoints),0)
    else:
        xp = round((totalScorePointsSeriousChallenge + totalScorePointsWarmupChallenge  + totalScorePointsActivityPoints + totalScoreSkillPoints),0)
        
    return (studentId,xp)

class TimePeriods:
    from django.utils import timezone
    from datetime import timedelta

    ''' TimePeriods enum starting at 1500.'''
    daily = 1500 # Runs every day at midnight
    weekly = 1501 # Runs every Sunday at midnight
    beginning_of_time = 1502 # Runs only once
    daily_test = 1599
    timePeriods = {
        daily_test:{
            'index': daily_test,
            'name': 'daily_test',
            'displayName': 'Every 2 Minutes (For Testing)',
            'schedule': get_or_create_schedule(
                        minute='*', hour='*', day_of_week='*', 
                        day_of_month='*', month_of_year='*'),
            'datetime': lambda: timezone.make_aware(timezone.now() - timedelta(minutes=2))
        },
        daily:{
            'index': daily,
            'name': 'daily',
            'displayName': 'Daily at Midnight',
            'schedule': get_or_create_schedule(
                        minute='0', hour='0', day_of_week='*', 
                        day_of_month='*', month_of_year='*'),
            'datetime': lambda: timezone.make_aware(timezone.now() - timedelta(days=1))
        },
        weekly:{
            'index': weekly,
            'name': 'weekly',
            'displayName': 'Weekly on Sundays at Midnight',
            'schedule': get_or_create_schedule(minute="0", hour="0", day_of_week='0'),
            'datetime': lambda: timezone.make_aware(timezone.now() - timedelta(days=7))
        },
        beginning_of_time:{
            'index': beginning_of_time,
            'name': 'beginning_of_time',
            'displayName': 'Only once at Midnight',
            'schedule': get_or_create_schedule(minute="0", hour="0"),
            'datetime': lambda: None
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
    

    periodicVariables = {
        highest_earner: {
            'index': highest_earner,
            'name': 'highest_earner',
            'displayName': 'Highest VC Earner',
            'description': 'Calculates the Highest Earner(s) of students based on the virtual currency they have earned',
            'function': calculate_student_earnings,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        student_warmup_pratice: {
            'index': student_warmup_pratice,
            'name': 'student_warmup_pratice',
            'displayName': 'Student Practice Warm-up Challenges',
            'description': 'Retrieves the amount of times students has practice different Warm-up challenges',
            'function': calculate_student_warmup_practice,
            'task_type': 'Badges.periodicVariables.periodic_task',
        },
        unique_warmups: {
            'index': unique_warmups,
            'name': 'unique_warmups',
            'displayName': 'Student Unique Warm-up Challenges Completed with a Score > 60%',
            'description': 'Retrieves the amount of unique Warm-up Challenges completed by students with a score greater than 60%',
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
        }
    }

