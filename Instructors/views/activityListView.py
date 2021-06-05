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

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def createContextForActivityList(request, context_dict, currentCourse):
    # TODO: This whole file needs to be cleaned/refactored
    activitiesInCategory = []
    categoryNames = []
    categoryIds = []
    categoryWeights = []
    
    defaultCat = ActivitiesCategory.objects.filter(name=uncategorized_activity, courseID=currentCourse).first()
    if defaultCat == None:
        defaultCat = ActivitiesCategory()
        defaultCat.name = uncategorized_activity
        defaultCat.courseID = currentCourse
        defaultCat.save()

    categories = ActivitiesCategory.objects.filter(courseID=currentCourse).order_by("catPosition")

    if request.method == "GET" or request.POST.get('actCat') == "all" or request.POST.get('actCat') == None:

        for cat in categories:
            if cat.name != uncategorized_activity:
                cat_activities = category_activities(cat, currentCourse)
                categoryNames.append(cat.name)
                categoryIds.append(cat.categoryID)
                if context_dict['ccparams'].xpWeightAPoints > 0:
                    categoryWeights.append(cat.xpWeight)
                else:
                    categoryWeights.append(None)
                activitiesInCategory.append(cat_activities)
        
        # Add uncategorized activity last
        cat_activities = category_activities(defaultCat, currentCourse)
        categoryNames.append(defaultCat.name)
        categoryIds.append(defaultCat.categoryID)
        if context_dict['ccparams'].xpWeightAPoints > 0:
            categoryWeights.append(cat.xpWeight)
        else:
            categoryWeights.append(None)
        activitiesInCategory.append(cat_activities)

        context_dict['currentCat'] = "all"
    elif request.method == "POST":
        filterCategory = request.POST.get('actCat')
        if filterCategory is not None:
            cat = ActivitiesCategory.objects.get(
                pk=filterCategory, courseID=currentCourse)
            cat_activities = category_activities(cat, currentCourse)
            activitiesInCategory.append(cat_activities)
            categoryNames.append(cat.name)
            categoryIds.append(cat.categoryID)
            if context_dict['ccparams'].xpWeightAPoints > 0:
                categoryWeights.append(cat.xpWeight)
            else:
                categoryWeights.append(None)
            context_dict['currentCat'] = cat

    context_dict["categories_range"] = list(zip(activitiesInCategory, categoryIds, categoryNames, categoryWeights))
    
    context_dict['categories'] = categories

    return context_dict


def category_activities(category, current_course):

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
    return list(zip(activity_IDs, activity_Names, descriptions, start_Timestamp, end_Timestamp, deadline, points, activityPositions))


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
