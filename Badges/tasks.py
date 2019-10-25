from django.conf import settings
from Badges.celeryApp import app

@app.task
def process_event_offline(eventpk, minireq, student, objectId):
    from Badges.events import process_event_actual
    return process_event_actual(eventpk, minireq, student, objectId)

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

@app.task(ignore_result=True)
def process_expired_serious_challenges(course_id, user_id, challenge_id, due_date, timezone):
    from Instructors.models import Challenges, Courses
    from Instructors.views.utils import localizedDate
    from Students.models import StudentRegisteredCourses
    from Badges.events import register_event_simple
    from Badges.enums import Event
    from django.contrib.auth.models import User
    from datetime import datetime

    course = Courses.objects.get(pk=int(course_id))
    currentTime = localizedDate(None, str(datetime.utcnow().replace(microsecond=0)), "%Y-%m-%d %H:%M:%S", timezone)

    challenge = Challenges.objects.filter(courseID=course, challengeID=challenge_id).first()
    # If the challenge is deleted don't calculate the send event
    if challenge:
        print("Passed Due Date: {}".format(due_date))
        print("Challenge Due Date: {}".format(challenge.dueDate))
        print("Current Time: {}".format(currentTime))
        # If the due date hasn't changed and the current time is at or passed the due date send the event
        if (due_date == challenge.dueDate and currentTime >= challenge.dueDate):
            # Don't send to test students
            registeredStudents = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)

            for student in registeredStudents:
                mini_req = {
                    'currentCourseID': course_id,
                    'user': User.objects.get(pk=int(user_id)).username,
                }
                register_event_simple(Event.challengeExpiration, mini_req, student.studentID, challenge.challengeID)
                print("Registered Event: Challenge Expiration Event, Student: " + str(student.studentID) + ", Challenge: " + str(challenge.challengeID))

def create_due_date_process(request, challenge_id, due_date, tz_info):
    ''' This will register a task to be called when a due date has been reach for a particular challenge'''

    from datetime import timedelta
    from django.utils.timezone import make_naive
    from Instructors.views.utils import localizedDate
    # Make date naive since celery eta accepts only naive datetimes then localize it
    due_date = make_naive(due_date)
    localized_due_date = localizedDate(request, str(due_date), "%Y-%m-%d %H:%M:%S")
    # Setup the task and run at a later time (due_date)
    # Will delete itself after one minute once it has finished running
    timezone = request.session['django_timezone']

    process_expired_serious_challenges.apply_async(kwargs={'course_id': request.session['currentCourseID'],
            'user_id': request.user.id,
            'challenge_id': challenge_id,
            'due_date': localized_due_date,
            'timezone': timezone,
            }, eta=localized_due_date, expires=localized_due_date + timedelta(minutes=1), serializer='pickle')

            
if settings.CELERY_ENABLED:
    schedule_celery_task_checker()

