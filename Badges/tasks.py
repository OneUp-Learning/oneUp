from django.conf import settings

import Badges.datamine_tasks
from Badges.celeryApp import app
from Badges.models import CeleryTestResult
from Students.views.utils import getLevelFromXP


@app.task
def process_event_offline(eventpk, minireq, student, objectId):
    from Badges.events import process_event_actual
    process_event_actual(eventpk, minireq, student, objectId)


@app.task(ignore_result=True)
def check_celery_tasks():
    ''' This will go through the CeleryTaskLogs and check to see if any celery tasks
        did not run in their given time period. It will then run those tasks
        using the parameters from the celery task log to call peroidic task function.

        This celery task will run every 30 minutes.

        Note: Possible a task will run twice at once if celery hasn't been running for a long time (greater than the task time period).
        Celery beat will schedule this task and the periodic task to be run at the moment celery is back up and running
        since it figures out both tasks missed their time because celery wasn't running.

        A quick fix would be to disable the "check_celery_task" in PeriodicTask table in admin interface,
        start celery, then re-enable it after the periodic tasks that missed their time has finished running.
    '''
    from Badges.models import CeleryTaskLog
    from Badges.periodicVariables import periodic_task, TimePeriods
    from django_celery_beat.models import PeriodicTask
    import json

    celery_task_entries = CeleryTaskLog.objects.all()
    # Loop throught logs
    for entry in celery_task_entries:
        # Check if periodic task is there, if not remove entry from log and continue (case when periodic task is deleted)
        p_task = PeriodicTask.objects.filter(name=entry.taskID).first()
        if p_task is None:
            print("DELETED LOG NONE")
            entry.delete()
            continue

        # Check if periodic task kwargs are the same as the parameters, if not remove entry and continue (case when periodic task is changed but id is the same)
        kwargs = json.loads(p_task.kwargs)
        parameters = json.loads(entry.parameters)
        if parameters != kwargs:
            print("DELETED LOG {} - Kwargs doesn't match".format(p_task.name))
            print(f"{parameters}\n\n{kwargs}")
            entry.delete()
            continue

        # Check if timestamp of log is within periodic task time period
        log_timestamp = entry.timestamp
        period_index = parameters['period_index']
        time_range = TimePeriods.timePeriods[period_index]['datetime']()

        # Double check if the time period is of beginning_of_time. There should be no log for this type
        if time_range is None:
            print("DELETED LOG {} - Time Period is beginning of time".format(p_task.name))
            entry.delete()
            continue

        # If not, call periodic_task with parameters (entry log will get updated by this call, hopefully)
        if log_timestamp.replace(microsecond=0, second=0) < time_range.replace(microsecond=0, second=0):
            print("RE RUN LOG TASK {}".format(p_task.name))
            periodic_task(parameters['unique_id'], parameters['variable_index'], parameters['course_id'],
                          parameters['period_index'], parameters['number_of_top_students'], parameters['threshold'],
                          parameters['operator_type'], parameters['is_random'], parameters['is_leaderboard'],
                          parameters['badge_id'], parameters['virtual_currency_amount'], parameters['save_results'])


def schedule_celery_task_checker():
    ''' This will create the celery task (check_celery_task) if it doesn't exist and will schedule it to run every 30 minutes '''
    from django_celery_beat.models import PeriodicTask
    from Badges.periodicVariables import get_or_create_schedule

    periodic_task, _ = PeriodicTask.objects.get_or_create(
        name='check_celery_tasks',
        task='Badges.tasks.check_celery_tasks',
        crontab=get_or_create_schedule(minute='*/30'),
    )


def refresh_xp(student_reg_course):
    if settings.CELERY_ENABLED:
        celery_calculate_xp.delay(student_reg_course.pk)
    else:
        celery_calculate_xp(student_reg_course.pk)


@app.task
def celery_calculate_xp(student_reg_course_id):
    from Students.models import StudentRegisteredCourses
    from Badges.models import CourseConfigParams
    import decimal
    import json
    from notify.signals import notify
    from Badges.enums import Event
    from Badges.events import register_event_simple

    student_reg_course = StudentRegisteredCourses.objects.get(
        pk=int(student_reg_course_id))
    xp = calculate_xp(student_reg_course)
    ccP = CourseConfigParams.objects.get(courseID=student_reg_course.courseID)
    student_reg_course.xp = xp
    if ccP.levelingUsed:
        # if student_reg_course.level == 0:
        level = getLevelFromXP(ccP.levelTo1XP,xp,ccP.nextLevelPercent)
        if level > student_reg_course.level:
            student_reg_course.level = level
            notify.send(None, recipient=student_reg_course.studentID.user, actor=student_reg_course.studentID.user, verb=f'You have leveled up to level ' + str(level), nf_type='level', extra=json.dumps(
                   {"course": str(student_reg_course.courseID.courseID), "name": str(student_reg_course.courseID.courseName), "related_link": '/oneUp/students/StudentCourseHome'}))
            # for event
            mini_req = {
                'currentCourseID': student_reg_course.cgitourseID.courseID,
                'user': student_reg_course.studentID.user.username,
                'timezone': None,
            }
            # register event
            # register_event_simple(
            #    Event.levelUp, mini_req, student_reg_course.studentID, level)

    student_reg_course.save()


def calculate_xp(student_reg_course, gradeWarmup=False, gradeSerious=False, gradeActivity=False):
    from Badges.models import CourseConfigParams, LeaderboardsConfig
    from Instructors.models import Challenges, Activities, CoursesSkills, Skills
    from Students.models import StudentChallenges, StudentActivities, StudentCourseSkills
    from Students.views import classResults
    from Instructors.constants import uncategorized_activity

    xp = 0
    xpWeightSP = 0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    course = student_reg_course.courseID
    studentId = student_reg_course.studentID
    ccparamsList = CourseConfigParams.objects.filter(courseID=course)

    # If result only, we only want to search from the start of the course
    # else, we will search based on howFarBack (see below)
    startOfTime = True

    # Specify if the xp should be calculated based on max score or first attempt
    xpSeriousMaxScore = True
    xpWarmupMaxScore = True
    challengeClassmates = False
    if len(ccparamsList) > 0:
        cparams = ccparamsList[0]
        xpWeightSP = cparams.xpWeightSP
        xpWeightSChallenge = cparams.xpWeightSChallenge
        xpWeightWChallenge = cparams.xpWeightWChallenge
        xpWeightAPoints = cparams.xpWeightAPoints
        xpSeriousMaxScore = cparams.xpCalculateSeriousByMaxScore
        xpWarmupMaxScore = cparams.xpCalculateWarmupByMaxScore

    # SERIOUS CHALLENGES
    # Get the earned points
    earnedSeriousChallengePoints = 0

    courseChallenges = Challenges.objects.filter(
        courseID=course, isGraded=True).order_by('challengePosition')
    for challenge in courseChallenges:
        seriousChallenge = StudentChallenges.objects.filter(
            studentID=studentId, courseID=course, challengeID=challenge)

        # Ignore challenges that have invalid total scores
        if seriousChallenge and seriousChallenge[0].challengeID.totalScore < 0:
            continue
        # Get the scores for this challenge then either add the max score
        # or the first score to the earned points variable
        gradeID = []
        for serious in seriousChallenge:
            # get the score + adjustment + bonus
            gradeID.append(float(serious.getScoreWithBonus()))

        if xpSeriousMaxScore and gradeID:
            earnedSeriousChallengePoints += max(gradeID)
        elif gradeID:
            earnedSeriousChallengePoints += float(
                seriousChallenge.first().getScoreWithBonus())

    # Weighting the total serious challenge points to be used in calculation of the XP Points
    weightedSeriousChallengePoints = earnedSeriousChallengePoints * xpWeightSChallenge / 100
    print(weightedSeriousChallengePoints)

    # WARMUP CHALLENGES
    # Get the earned points
    earnedWarmupChallengePoints = 0

    courseChallenges = Challenges.objects.filter(
        courseID=course, isGraded=False)
    for challenge in courseChallenges:

        warmupChallenge = StudentChallenges.objects.filter(
            studentID=studentId, courseID=course, challengeID=challenge)
        # print("Challenge List ", warmupChallenge)
        # Ignore challenges that have invalid total scores
        if warmupChallenge and warmupChallenge[0].challengeID.totalScore < 0:
            continue

        # Get the scores for this challenge then either add the max score
        # or the first score to the earned points variable
        gradeID = []
        for warmup in warmupChallenge:
            gradeID.append(float(warmup.testScore))

        if xpWarmupMaxScore and gradeID:
            earnedWarmupChallengePoints += max(gradeID)
        elif gradeID:
            earnedWarmupChallengePoints += float(
                warmupChallenge.first().testScore)

    # Weighting the total warmup challenge points to be used in calculation of the XP Points
    weightedWarmupChallengePoints = earnedWarmupChallengePoints * \
        xpWeightWChallenge / 100      # max grade for this challenge
    print(weightedWarmupChallengePoints)
    # ACTIVITIES
    # Get the earned points
    earnedActivityPoints = 0

    courseActivities = Activities.objects.filter(
        courseID=course, isGraded=True)
    for activity in courseActivities:
        studentActivities = StudentActivities.objects.filter(
            studentID=studentId, courseID=course, activityID=activity)

        xpWeightCategory = 1
        if activity.category.name != uncategorized_activity:
            xpWeightCategory = activity.category.xpWeight

        # Get the scores for this challenge then add the max score
        # to the earned points variable
        gradeID = []
        for studentActivity in studentActivities:
            gradeID.append(float(studentActivity.getScoreWithBonus()))

        if gradeID:
            earnedActivityPoints += max(gradeID) * float(xpWeightCategory)

    # Weighting the total activity points to be used in calculation of the XP Points
    weightedActivityPoints = earnedActivityPoints * xpWeightAPoints / 100
    print(weightedActivityPoints)
    # SKILL POINTS
    # Get the earned points
    earnedSkillPoints = 0

    cskills = CoursesSkills.objects.filter(courseID=course)
    for sk in cskills:

        skill = Skills.objects.get(skillID=sk.skillID.skillID)

        sp = StudentCourseSkills.objects.filter(
            studentChallengeQuestionID__studentChallengeID__studentID=studentId, skillID=skill)

        if sp:
            # Get the scores for this challenge then add the max score
            # to the earned points variable
            gradeID = []

            for p in sp:
                gradeID.append(int(p.skillPoints))

            sumSkillPoints = sum(gradeID, 0)
            earnedSkillPoints += sumSkillPoints

    # Weighting the total skill points to be used in calculation of the XP Points
    weightedSkillPoints = earnedSkillPoints * xpWeightSP / 100
    print(weightedSkillPoints)
    # Return the xp and/or required variables rounded to 1 decimal place
    xp = 0
    if gradeWarmup:
        xp += weightedWarmupChallengePoints
    if gradeSerious:
        xp += weightedSeriousChallengePoints
    if gradeActivity:
        xp += weightedActivityPoints

    if not gradeSerious and not gradeWarmup and not gradeActivity:
        xp += weightedSeriousChallengePoints + weightedWarmupChallengePoints + \
            weightedActivityPoints + weightedSkillPoints

    xp = round(xp, 1)
    return xp


@app.task(ignore_result=True)
def process_expired_serious_challenges(course_id, user_id, challenge_id, due_date, timezone):
    from Instructors.models import Challenges, Courses
    from Instructors.views.utils import current_localtime, datetime_to_local
    from Students.models import StudentRegisteredCourses
    from Badges.events import register_event_simple
    from Badges.enums import Event
    from django.contrib.auth.models import User
    from datetime import datetime

    course = Courses.objects.get(pk=int(course_id))
    currentTime = current_localtime(tz=timezone)

    challenge = Challenges.objects.filter(
        courseID=course, challengeID=challenge_id).first()
    # If the challenge is deleted don't calculate the send event
    if challenge:
        print("Passed Due Date: {}".format(due_date))
        print("Challenge Due Date: {}".format(challenge.dueDate))
        print("Current Time: {}".format(currentTime))
        # If the due date hasn't changed and the current time is at or passed the due date send the event
        if due_date == challenge.dueDate and currentTime >= datetime_to_local(challenge.dueDate, tz=timezone):
            # Don't send to test students
            registeredStudents = StudentRegisteredCourses.objects.filter(
                courseID=course, studentID__isTestStudent=False)

            for student in registeredStudents:
                mini_req = {
                    'currentCourseID': course_id,
                    'user': User.objects.get(pk=int(user_id)).username,
                    'timezone': timezone
                }
                register_event_simple(
                    Event.challengeExpiration, mini_req, student.studentID, challenge.challengeID)
                print("Registered Event: Challenge Expiration Event, Student: " +
                      str(student.studentID) + ", Challenge: " + str(challenge.challengeID))


def create_due_date_process(request, challenge_id, due_date, tz_info):
    ''' This will register a task to be called when a due date has been reach for a particular challenge'''
    if not settings.CELERY_ENABLED:
        return
        
    from datetime import timedelta
    from django.utils.timezone import make_naive, get_current_timezone_name
    from Instructors.views.utils import str_datetime_to_local
    # Make date naive since celery eta accepts only naive datetimes then localize it
    # due_date = make_naive(due_date)
    #due_date = make_naive(due_date).replace(microsecond=0)
    localized_due_date = str_datetime_to_local(str(due_date), to_format="%Y-%m-%d %H:%M:%S")
    # Setup the task and run at a later time (due_date)
    # Will delete itself after one minute once it has finished running
    timezone = get_current_timezone_name()

    process_expired_serious_challenges.apply_async(kwargs={'course_id': request.session['currentCourseID'],
                                                           'user_id': request.user.id,
                                                           'challenge_id': challenge_id,
                                                           'due_date': localized_due_date,
                                                           'timezone': timezone,
                                                           }, eta=localized_due_date, expires=localized_due_date + timedelta(minutes=1), serializer='pickle')


@app.task(ignore_result=True)
def process_expired_goal(course_id, student_id, goal_id, end_date, timezone):
    from Instructors.models import Courses
    from Instructors.views.utils import current_localtime, datetime_to_local
    from Students.views.goalsListView import goal_type_to_name
    from Students.models import Student, StudentGoalSetting
    from notify.signals import notify
    from datetime import datetime, timedelta
    import json

    course = Courses.objects.get(pk=int(course_id))
    student = Student.objects.get(pk=int(student_id))
    currentTime = current_localtime(tz=timezone)

    goal = StudentGoalSetting.objects.filter(
        courseID=course, studentID=student).first()
    # If the goal is deleted don't calculate the send event
    if goal:
        goal_end_date = datetime_to_local(goal.timestamp, tz=timezone) + timedelta(days=7)

        print("Passed End Date: {}".format(end_date))
        print("Goal End Date: {}".format(goal_end_date))
        print("Current Time: {}".format(currentTime))
        # If the end date hasn't changed and the current time is at or passed the end date send the event
        if not goal.completed and end_date == goal_end_date and currentTime >= goal_end_date:
            print("Sending goal notification")
            notify.send(None, recipient=student.user, actor=student.user, verb=f"{goal_type_to_name(goal.goalVariable)} personal goal is due", nf_type='goal', extra=json.dumps(
                {"course": str(course.courseID), "name": str(course.courseName), "related_link": '/oneUp/students/goalslist'}))

            # Maybe can register a event that a goal has expired


def create_goal_expire_event(request, student_id, goal_id, end_date, tz_info):
    ''' This will register a task to be called when a goal end time has been reach'''
    if not settings.CELERY_ENABLED:
        return

    from datetime import timedelta
    from django.utils.timezone import make_naive
    from Instructors.views.utils import str_datetime_to_local
    # Make date naive since celery eta accepts only naive datetimes then localize it
    end_date = make_naive(end_date).replace(microsecond=0)
    localized_end_date = str_datetime_to_local(str(end_date), to_format="%Y-%m-%d %H:%M:%S")
    # Setup the task and run at a later time (end_date)
    # Will delete itself after one minute once it has finished running
    
    process_expired_goal.apply_async(kwargs={'course_id': request.session['currentCourseID'],
                                             'student_id': student_id,
                                             'goal_id': goal_id,
                                             'end_date': localized_end_date,
                                             'timezone': tz_info,
                                             }, eta=localized_end_date, expires=localized_end_date + timedelta(minutes=1), serializer='pickle')


if settings.CELERY_ENABLED:
    schedule_celery_task_checker()


@app.task
def testTask(uniqid, sequence):
    ctr = CeleryTestResult()
    ctr.uniqid = uniqid
    ctr.sequence = sequence
    ctr.save()
    return uniqid, sequence

@app.task(ignore_result=True)
def recalculate_student_virtual_currency_total_offline(student_id,course_id):
    from Students.models import Student
    from Instructors.models import Courses
    student = Student.objects.get(pk=student_id)
    course = Courses.objects.get(pk=course_id)
    from Badges.events import recalculate_student_virtual_currency_total
    recalculate_student_virtual_currency_total(student,course)
