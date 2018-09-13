from django_celery_beat.models import CrontabSchedule, PeriodicTask
from Badges.tasks import app
import json
import random

def setup_periodic_variable(unique_id, variable_index, course, time_period, number_of_top_students=None, threshold=None, operator_type=None, is_random=None, badge_id=None, virtual_currency_amount=None):
    ''' Creates Periodic Task if not created with the provided periodic variable function and schedule.'''
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]
    PeriodicTask.objects.get_or_create(
        name=periodic_variable['name']+'_'+str(unique_id),
        kwargs=json.dumps({
            'variable_index': variable_index,
            'course_id': course.courseID,
            'time_period': time_period,
            'number_of_top_students': number_of_top_students,
            'threshold': threshold,
            'operator_type': operator_type,
            'is_random': is_random,
            'badge_id': badge_id,
            'virtual_currency_amount': virtual_currency_amount
        }),
        task=periodic_variable['task_type'],
        crontab=TimePeriods.timePeriods[time_period]['schedule'],
    )
def delete_periodic_task(variable_index, course, time_period, number_of_top_students=None,threshold=None, operator_type=None, is_random=None, badge_id=None, virtual_currency_amount=None):
    ''' Deletes Periodic Task when rule or badge is deleted'''
    PeriodicTask.objects.filter(kwargs__contains=json.dumps({
            'variable_index': variable_index,
            'course_id': course.courseID,
            'time_period': time_period,
            'number_of_top_students': number_of_top_students,
            'threshold': threshold,
            'operator_type': operator_type,
            'is_random': is_random,
            'badge_id': badge_id,
            'virtual_currency_amount': virtual_currency_amount
        })).delete()

def get_course(course_id):
    ''' Method to get the course object from course id'''
    from Instructors.models import Courses
    course = Courses.objects.get(pk=int(course_id))
    return course


@app.task(ignore_result=True)
def ranking_task(variable_index, course_id, time_period, number_of_top_students, threshold, operator_type, is_random, badge_id=None, virtual_currency_amount=None): 
    ''' Celery task which runs based on the time period (weekly, daily, etc). This task either does one of the following
        with the results given by the periodic variable function:
            1. Takes the top number of students specified by number_of_top_students variable
            2. Takes the students above a threshold based on students results
            3. Takes a student at random above a threshold based on students results
            3. Takes a student a random
        Then awards the student(s) with a badge or virtual currency.

        If badge_id is provided the student(s) will be given a badge.
        If virtual_currency_amount is provied the student(s) will be given virtual currency.
        Both can be provied to give both to student(s).

        Note: operator_type is string and is_random is a boolean. Everything else should be an integer
    '''
    from Students.models import StudentRegisteredCourses

    # Get the course object and periodic variable
    course = get_course(course_id)
    periodic_variable = PeriodicVariables.periodicVariables[variable_index]

    # Get all the students in this course
    students = StudentRegisteredCourses.objects.filter(courseID=course)
    rank = []
    # Evaluate each student based on periodic variable function
    for student_in_course in students:
        rank.append(periodic_variable['function'](course, student_in_course.studentID, periodic_variable))


    print("Results: {}".format(rank))
    # Filter out students based on periodic badge/vc rule settings
    rank = filter_students(rank, number_of_top_students, threshold, operator_type, is_random)
    print("Filtered: {}".format(rank))
    # Give award to students
    award_students(rank, badge_id, virtual_currency_amount)

def filter_students(students, number_of_top_students, threshold, operator_type, is_random):
    ''' Filters out students based on parameters if they are not None.
        number_of_top_students: gets the top number of students wanted
        threshold & operator_type: gets the students which are above/at a threshold
        is_random: randomly chooses a student. Can be paired with threshold.
    '''

    if students:
        if number_of_top_students:
            # Sort the students
            students.sort(key=lambda tup: tup[1])
            # Check if what we want is greater than the number of students
            if len(students) >= number_of_top_students:
                # Only select the top number of students
                students = students[:number_of_top_students]
        elif threshold:
            operatorType = {
                '>=': lambda x, y : x >= y,
                '>' : lambda x, y : x > y,
                '=' : lambda x, y : x == y
            }
            # Filter students based on if their result passes the threshold
            students = [(student, val) for student, val in students if operatorType[operator_type](val, threshold)]
            if is_random and students:
                # If random, choose one student and remove everyone else
                students = random.sample(students, 1)
        elif is_random:
            # If random, choose one student and remove everyone else
            students = random.sample(students, 1)
    return students

def award_students(students, badge_id=None, virtual_currency_amount=None):
    ''' Awards students a badge or virtual currency or both.'''

    from notify.signals import notify  
    from Students.models import StudentBadges
    from Badges.models import BadgesInfo
    from Instructors.views.utils import utcDate

    for student, result in students:
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
            
            # Notify student of badge award 
            notify.send(None, recipient=student.user, actor=student.user, verb='You won the '+badge.badgeName+' badge', nf_type='Badge')
            
        # Give award of virtual currency
        if virtual_currency_amount:
            if virtual_currency_amount > 0:
                student.virtualCurrencyAmount += virtual_currency_amount
                student.save()
                # Notify student of VC award 
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

