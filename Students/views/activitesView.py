'''
Created on Aug 28, 2017

@author: jevans116
'''
import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from Badges.enums import ObjectTypes
from Badges.models import ProgressiveUnlocking
from Badges.systemVariables import logger
from Instructors.models import Activities, ActivitiesCategory
from Instructors.views.utils import current_localtime, datetime_to_local
from Students.models import StudentActivities, StudentProgressiveUnlocking
from Students.views.utils import studentInitialContextDict


@login_required
def ActivityList(request):

    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict, currentCourse = studentInitialContextDict(request)

    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:
        current_course = request.session['currentCourseID']

        categories_list = []
        cats = []
        categories_names = []
        isUnlocked = []
        ulockingDescript = []

        studentId = context_dict['student']  # get student
        categories = ActivitiesCategory.objects.filter(
            courseID=current_course).order_by('catPosition')

        for cat in categories:
            cats.append(cat)

        # Displaying the list of challenges from database
        if request.method == "GET" or request.POST.get('actCat') == "all":
            context_dict['currentCat'] = "all"

        elif request.method == "POST":
            filterCategory = request.POST.get('actCat')
            if filterCategory is not None:
                categories = ActivitiesCategory.objects.filter(
                    pk=filterCategory, courseID=current_course)
                context_dict['currentCat'] = categories
            else:
                context_dict['currentCat'] = "all"

        for category in categories:
            print("cat name")
            print(category.name)
            cat_activities = category_activities(
                category, studentId, current_course)

            if cat_activities:
                categories_list.append(cat_activities)
                categories_names.append(category.name)

            # Progressvie Unlocking
            studentPUnlocking = StudentProgressiveUnlocking.objects.filter(
                studentID=studentId, objectID=category.pk, objectType=ObjectTypes.activityCategory, courseID=currentCourse).first()
            if studentPUnlocking:
                isUnlocked.append(studentPUnlocking.isFullfilled)
                ulockingDescript.append(
                    studentPUnlocking.pUnlockingRuleID.description)
            else:
                isUnlocked.append(True)
                ulockingDescript.append('')

        context_dict["categories"] = cats
        context_dict["categories_range"] = zip(
            categories_list, categories_names, isUnlocked, ulockingDescript)

    return render(request, 'Students/ActivityList.html', context_dict)


def category_activities(category, studentId, current_course):

    activites = []
    graded_acitvities = []
    points = []
    activity_points = []
    submit_status = []
    activity_date_status = []
    activity_due_date = []
    isUnlocked = []
    unlockDescript = []

    activity_objects = Activities.objects.filter(
        category=category, courseID=current_course)

    for act in activity_objects:
        # if today is after the data it was assigninged display it
        # logger.debug(timezone.localtime(act.startTimestamp))

        # Filter out if current time is not in range
        if act.hasStartTimestamp and datetime_to_local(act.startTimestamp) > current_localtime():
            continue
        if act.hasEndTimestamp and datetime_to_local(act.endTimestamp) <= current_localtime():
            continue
        
        activites.append(act)
        graded_acitvities.append(act.isGraded)
        act_graded = [act.isGraded]

        if act.isGraded:
            activity_points.append(round(act.points))
        else:
            activity_points.append(None)
            
        if act.hasDeadline:
            activity_due_date.append(act.deadLine)
        else:
            activity_due_date.append(None)

        if not act.hasDeadline:
            activity_date_status.append("")
        elif datetime_to_local(act.deadLine) <= current_localtime():
            activity_date_status.append("Overdue Activity")
        else:
            activity_date_status.append("Upcoming Activity")
        # get the activity record for this student 
        if StudentActivities.objects.filter(studentID=studentId, activityID=act):
            student_act = StudentActivities.objects.get(
                studentID=studentId, activityID=act)
            if student_act.graded:
                points.append(str(round(student_act.getScoreWithBonus())))
            else:
                points.append("-")
            if student_act.submitted:
                if act.hasDeadline and datetime_to_local(student_act.submissionTimestamp) > datetime_to_local(act.deadLine):
                    submit_status.append("Late Submission")
                else:
                    submit_status.append("Submitted")
        else: # Student has not yet uploaded
            points.append("-")
            if act.isGraded or act.isFileAllowed: #if the activity will be graded or Upload is enabled
                if act.hasDeadline and (datetime_to_local(act.deadLine) <= current_localtime()): #Has a deadline
                    submit_status.append("Missing")# if we are past the deadline, append Missing
                else:
                    submit_status.append("Not Yet Uploaded")
            else:
                submit_status.append("")

        # Progessive Unlocking
        try:
            oType = ObjectTypes.activity

            studentUnlockings = StudentProgressiveUnlocking.objects.filter(
                studentID=studentId, courseID=current_course, objectType=oType, objectID=act.pk)

            unlockingRules = ProgressiveUnlocking.objects.filter(
                courseID=current_course, objectType=oType, objectID=act.pk)

            if studentUnlockings:
                for studentUnlocking in studentUnlockings:
                    if studentUnlocking.isFullfilled:
                        isUnlocked.append(studentUnlocking.isFullfilled)
                    else:
                        isUnlocked.append(studentUnlocking.isFullfilled)
                    break
            else:
                isUnlocked.append(True)

            if unlockingRules:
                for unlockingRule in unlockingRules:
                    unlockDescript.append(unlockingRule.description)
                    break
            else:
                unlockDescript.append('hi')

        except ObjectDoesNotExist:
            isUnlocked.append(True)
            unlockDescript.append('hi')

    return list(zip(activites, points, activity_points, submit_status, activity_date_status, activity_due_date, isUnlocked, unlockDescript, graded_acitvities, act_graded))
