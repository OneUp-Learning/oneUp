from django_celery_beat.models import CrontabSchedule, PeriodicTask
from Badges.tasks import app
import json


def setup_periodic_variable(variable_index, course, time_period, number_of_top_students=3, badge_id=None, virtual_currency_amount=None):
    ''' Creates Periodic Task if not created with the provided periodic variable function and schedule.'''
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    PeriodicTask.objects.get_or_create(
        name=periodic_variable['name'],
        kwargs=json.dumps({
            'variable_index': variable_index,
            'course_id': course.courseID,
            'time_period': time_period,
            'number_of_top_students': number_of_top_students,
            'badge_id': badge_id,
            'virtual_currency_amount': virtual_currency_amount
        }),
        task=periodic_variable['task_type'],
        crontab=TimePeriods.timePeriods[time_period]['schedule'],
    )
def delete_periodic_task(variable_index, course, time_period, number_of_top_students=3, badge_id=None, virtual_currency_amount=None):
    ''' Deletes Periodic Task when rule or badge is deleted'''
    PeriodicTask.objects.filter(kwargs__contains=json.dumps({
            'variable_index': variable_index,
            'course_id': course.courseID,
            'time_period': time_period,
            'number_of_top_students': number_of_top_students,
            'badge_id': badge_id,
            'virtual_currency_amount': virtual_currency_amount
        })).delete()

def get_course(course_id):
    ''' Method to get the course object from course id'''
    from Instructors.models import Courses
    course = Courses.objects.get(pk=int(course_id))
    return course


@app.task(ignore_result=True)
def ranking_task(variable_index, course_id, time_period, number_of_top_students, badge_id=None, virtual_currency_amount=None): 
    ''' Celery task which runs based on the time period (weekly, daily, etc). This task specifically ranks all the students
        in the course by the results which is given by a periodic variable function then takes the top number of students
        specified by number_of_top_students variable and gives the student(s) a award (Bdage or Virtual Currency).

        If badge_id is provided the student(s) will be given a badge.
        If virtual_currency_amount is provied the student(s) will be given virtual currency.
        Both can be provied to give both to student(s).

        Note: All method parameters should be a integer.
    '''
    from notify.signals import notify  
    from Students.models import StudentRegisteredCourses, StudentBadges
    from Badges.models import BadgesInfo
    from Instructors.views.utils import utcDate

    # Get the course object and periodic variable
    course = get_course(course_id)
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]

    # Get all the students in this course
    students = StudentRegisteredCourses.objects.filter(courseID=course)
    rank = []
    # Evaluate each student based on periodic variable function
    for student_in_course in students:
        rank.append(periodic_variable['function'](course, student_in_course.studentID, periodic_variable))

    # Sort by periodic variable results (student, value) and get top results based on number _of_rank
    rank.sort(key=lambda tup: tup[1])
    if len(rank) >= number_of_top_students:
        rank = rank[:number_of_top_students]
    
    print(rank)

    for student, result in rank:
        # Give award for either badge or virtual currency
        if badge_id:
            # Check if student has earned this badge
            studentBadges = StudentBadges.objects.filter(studentID = student, badgeID = badge_id)
            if studentBadges.exists():
                print("Badge already earned")
                return

            # If the badge has not already been earned, then award it 
            badge = BadgesInfo.objects.get(pk=badge_id)
   
            studentBadge = StudentBadges()
            studentBadge.studentID = student
            studentBadge.badgeID = badge
            studentBadge.objectID = 0
            studentBadge.timestamp = utcDate()
            studentBadge.save()
            
            # Test to make notifications 
            notify.send(None, recipient=student.user, actor=student.user, verb='You won the '+badge.badgeName+' badge', nf_type='Badge')
            
        # Give award of virtual currency
        if virtual_currency_amount:
            if virtual_currency_amount > 0:
                student.virtualCurrencyAmount += virtual_currency_amount
                student.save()
                notify.send(None, recipient=student.user, actor=student.user, verb='You won '+str(virtual_currency_amount)+' virtual bucks', nf_type='Increase VirtualCurrency')


def calculate_student_earnings(course, student, periodic_variable):
    ''' This calculates the student earnings of virtual currency since the last period.
        Earnings are defined by only what virtual currency they gained and not spent.'''
    
    print("Calculating Highest Earner") 
    from Students.models import StudentVirtualCurrency
    # Get the last time this periodic variable has ran
    last_ran = PeriodicTask.objects.get(task=periodic_variable['task_type']).last_run_at
    # Get the earnings for this student
    earnings = StudentVirtualCurrency.objects.filter(studentID = student, vcRuleID__courseID = course)
    # If this is not the first time running, only get the earnings since last ran
    if last_ran:
        earnings = earnings.filter(timestamp__gte=last_ran)
        
    # Get the total earnings only if they have earned more than 0
    total = sum(int(earn.value) for earn in earnings if earn.value > 0)
   
    print("Course: {}".format(course))
    print("Student: {}".format(student))
    print("Periodic Variable: {}".format(periodic_variable))
    print("Last Ran: {}".format(last_ran))
    print("Total Earnings: {}".format(total))
    return (student, total)

class TimePeriods:
    ''' TimePeriods enum starting at 1500.'''
    daily = 1500
    weekly = 1501
    timePeriods = {
        daily:{
            'index': daily,
            'name': 'daily',
            'displayName': 'Daily',
            'schedule': CrontabSchedule.objects.get_or_create(
                        minute='*/2', hour='*', day_of_week='*', 
                        day_of_month='*', month_of_year='*')[0]
        },
        weekly:{
            'index': weekly,
            'name': 'weekly',
            'displayName': 'Weekly',
            'schedule': CrontabSchedule.objects.get_or_create(day_of_week='0')[0]
        }
    }
class PeriodicVariables:
    '''PeriodicVariables enum starting at 1400.'''
    
    highest_earner = 1400

    periodicVariables = {
        highest_earner: {
            'index': highest_earner,
            'name': 'highest_earner',
            'displayName': 'Highest Earner',
            'description': 'Calculates the Highest Earner(s) of students based on the virtual currency they have earned',
            'function': calculate_student_earnings,
            'task_type': 'Badges.periodicVariables.ranking_task',
        }
    }

