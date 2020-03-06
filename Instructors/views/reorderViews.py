'''
Created on February 27, 2020

@author: Omar
'''

from django.http import JsonResponse
from Instructors.models import CoursesTopics, Challenges, Activities, ActivitiesCategory
import json
from Instructors.views import utils


def reorderTopics(request):
    ''' This view is called by an ajax function to reorder topics'''

    context_dict, currentCourse = utils.initialContextDict(request)

    print("reorderTopics")
    print(request.POST)
    if request.POST:
        topicIdsPositions = request.POST.getlist("topicIdsPositions[]")
        print("topicIdsPositions")
        print(topicIdsPositions)

        for topicIdPos in topicIdsPositions:
            idPos = topicIdPos.split("---")
            print(idPos)
            try:
                courseTopic = CoursesTopics.objects.get(
                    topicID__topicID=int(idPos[0]), courseID=currentCourse)
                courseTopic.topicPos = int(idPos[1])
                courseTopic.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def reorderChalls(request):
    ''' This view is called by an ajax function to reorder challenges'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        challIdsPositions = request.POST.getlist("challIdsPositions[]")

        for challIdPos in challIdsPositions:
            idPos = challIdPos.split("---")
            try:
                chall = Challenges.objects.get(
                    challengeID=int(idPos[0]), courseID=currentCourse)
                chall.challengePosition = int(idPos[1])
                chall.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def reorderCategories(request):
    ''' This view is called by an ajax function to reorder categories'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        catIdsPositions = request.POST.getlist("catIdsPositions[]")
        for catdPos in catIdsPositions:
            idPos = catdPos.split("---")

            try:
                cat = ActivitiesCategory.objects.get(
                    categoryID=int(idPos[0]), courseID=currentCourse)
                cat.catPosition = int(idPos[1])
                cat.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def reorderActivities(request):
    ''' This view is called by an ajax function to reorder activities'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        activityIdsPositions = request.POST.getlist("activityIdsPositions[]")
        for activityIdPos in activityIdsPositions:
            idPos = activityIdPos.split("---")

            try:
                activity = Activities.objects.get(
                    activityID=int(idPos[0]), courseID=currentCourse)
                activity.activityPosition = int(idPos[1])
                activity.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})
