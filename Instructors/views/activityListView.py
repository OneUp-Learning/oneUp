'''
Created on March 11, 2015

@author: dichevad
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Instructors.constants import uncategorized_activity
from Instructors.models import Activities, ActivitiesCategory
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Students.models import StudentActivities, StudentRegisteredCourses


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def createContextForActivityList(request, context_dict, currentCourse):
    # TODO: This whole file needs to be cleaned/refactored
    activity_ID = []
    activity_Name = []
    description = []
    points = []
    student_ID = []
    student_Name = []
    activitiesInCategory = []
    cats = []
    categoryNames = []
    categoryIds = []
    categoryWeights = []

    if ActivitiesCategory.objects.filter(name=uncategorized_activity, courseID=currentCourse).first() == None:
        defaultCat = ActivitiesCategory()
        defaultCat.name = uncategorized_activity
        defaultCat.courseID = currentCourse
        defaultCat.save()

    categories = ActivitiesCategory.objects.filter(courseID=currentCourse).order_by("catPosition")
    for cat in categories:
        cats.append(cat)

    if request.method == "GET" or request.POST.get('actCat') == "all" or request.POST.get('actCat') == None:

        '''categories_l = ActivitiesCategory.objects.filter(
            courseID=currentCourse)

        categories = []
        if categories_l:
            categories = list(categories_l)[1:] + \
                list(categories_l)[0:1]'''
        count = 1
        for cat in categories:
            if cat.name != uncategorized_activity:
                cat_activities = category_activities(count, cat, currentCourse)
                categoryNames.append(cat.name)
                categoryIds.append(cat.categoryID)
                if context_dict['ccparams'].xpWeightAPoints > 0:
                    categoryWeights.append(cat.xpWeight)
                else:
                    categoryWeights.append(None)
                activitiesInCategory.append(cat_activities)
                count += Activities.objects.filter(category=cat,
                                                courseID=currentCourse).count()
        
        # Add uncategorized activity last
        cat = ActivitiesCategory.objects.filter(name=uncategorized_activity, courseID=currentCourse).first()
        cat_activities = category_activities(count, cat, currentCourse)
        categoryNames.append(cat.name)
        categoryIds.append(cat.categoryID)
        if context_dict['ccparams'].xpWeightAPoints > 0:
            categoryWeights.append(cat.xpWeight)
        else:
            categoryWeights.append(None)
        activitiesInCategory.append(cat_activities)
        count += Activities.objects.filter(category=cat,
                                        courseID=currentCourse).count()

        activities = Activities.objects.filter(
            category=cat, courseID=currentCourse)
        for activity in activities:
            activity_ID.append(activity.activityID)  # pk
            activity_Name.append(activity.activityName)
            description.append(activity.description[:100])
            points.append(activity.points)
        context_dict['currentCat'] = "all"
    elif request.method == "POST":
        filterCategory = request.POST.get('actCat')
        if filterCategory is not None:
            count = 1
            cat = ActivitiesCategory.objects.get(
                pk=filterCategory, courseID=currentCourse)
            cat_activities = category_activities(count, cat, currentCourse)
            activitiesInCategory.append(cat_activities)
            categoryNames.append(cat.name)
            categoryIds.append(cat.categoryID)
            if context_dict['ccparams'].xpWeightAPoints > 0:
                categoryWeights.append(cat.xpWeight)
            else:
                categoryWeights.append(None)
            activities = Activities.objects.filter(
                category=filterCategory, courseID=currentCourse)
            for activity in activities:
                activity_ID.append(activity.activityID)  # pk
                activity_Name.append(activity.activityName)
                description.append(activity.description[:100])
                points.append(activity.points)
            context_dict['currentCat'] = cat

    context_dict["categories"] = cats
    context_dict["categories_range"] = list(zip(
        activitiesInCategory, categoryIds, categoryNames, categoryWeights))

    # The range part is the index numbers.
    context_dict['activity_range'] = list(zip(
        range(1, activities.count()+1), activity_ID, activity_Name, description, points))
    context_dict['activitesForCats'] = list(zip(
        range(1, activities.count()+1), activity_ID, activity_Name, description, points))

    # Get StudentID and StudentName for every student in the current course
    # This context_dict is used to populate the scrollable check list for student names
    studentCourse = StudentRegisteredCourses.objects.filter(
        courseID=request.session['currentCourseID'])
    for entry in studentCourse:
        student_ID.append(entry.studentID.id)
        student_Name.append((entry.studentID).user.get_full_name())
    context_dict['student_select_range'] = zip(student_ID, student_Name)
    context_dict['activity_select_range'] = zip(activity_ID, activity_Name)

    # Assignment History Section
    assignment_ID = []
    assignment_Name = []
    assignment_Recipient = []
    assignment_Points = []

    assignments = StudentActivities.objects.all().order_by('-studentActivityID')
    for assignment in assignments:
        assignment_ID.append(assignment.studentActivityID)  # pk
        assignment_Name.append(assignment.activityID.activityName)
        assignment_Recipient.append(assignment.studentID)
        assignment_Points.append(assignment.activityScore)

    context_dict['assignment_history_range'] = zip(range(1, assignments.count(
    )+1), assignment_Name, assignment_Recipient, assignment_Points, assignment_ID)

    categories = ActivitiesCategory.objects.filter(
        courseID=currentCourse).order_by("catPosition")
    context_dict['categories'] = categories

    return context_dict


def category_activities(count, category, current_course):

    activity_IDs = []
    activity_Names = []
    descriptions = []
    start_Timestamp = []
    end_Timestamp = []
    deadline = []
    points = []
    activityPositions = []

    activity_objects = Activities.objects.filter(
        category=category, courseID=current_course).order_by('activityPosition')
    print(activity_objects)
    for activity in activity_objects:
        activity_IDs.append(activity.activityID)  # pk
        activity_Names.append(activity.activityName)
        descriptions.append(activity.description[:100])
        points.append(round(activity.points))
        activityPositions.append(activity.activityPosition)

        if activity.hasStartTimestamp:
            start_Timestamp.append(activity.startTimestamp)
        else:
            start_Timestamp.append("")
        
        if activity.hasEndTimestamp:
            end_Timestamp.append(activity.endTimestamp)
        else:
            end_Timestamp.append("")

        if activity.hasDeadline:
            deadline.append(activity.deadLine)
        else:
            deadline.append("")
    last = count + len(activity_IDs)
    return list(zip(range(count, last), activity_IDs, activity_Names, descriptions, start_Timestamp, end_Timestamp, deadline, points, activityPositions))


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def activityList(request):

    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForActivityList(
        request, context_dict, currentCourse)

    return render(request, 'Instructors/ActivitiesList.html', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def reorderActivities(request):
    context_dict, currentCourse = initialContextDict(request)
    if request.POST:

        activityPositions = request.POST.getlist('activityPositions[]')
        activityIDs = request.POST.getlist('activityID[]')
        activityIDsAndPositions = zip(activityIDs, activityPositions)

        for activity, position in activityIDsAndPositions:
            activity = Activities.objects.get(activityID=activity)
            activity.activityPosition = position
            activity.save()

    return redirect('/oneUp/instructors/activitiesList')
