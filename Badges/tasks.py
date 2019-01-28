from celery import Celery

app = Celery('Badges',broker='amqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')
@app.task
def process_event_offline(eventpk, minireq, student, objectId):
    from Badges.events import process_event_actual
    return process_event_actual(eventpk, minireq, student, objectId)

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

            

