'''
Created on February 27, 2020

@author: Omar
'''

from django.http import JsonResponse
from Instructors.models import CoursesTopics, Challenges, Activities, ActivitiesCategory, ChallengesQuestions,FlashCardGroupCourse
from Badges.models import BadgesInfo, VirtualCurrencyCustomRuleInfo
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


def reorderQuestions(request):
    ''' This view is called by an ajax function to reorder questions'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        questionIdsPositions = request.POST.getlist("questionIdsPositions[]")
        for questionIdPos in questionIdsPositions:
            idPos = questionIdPos.split("---")

            try:
                question = ChallengesQuestions.objects.get(
                    questionID__questionID=int(idPos[0]), challengeID__courseID=currentCourse)
                question.questionPosition = int(idPos[1])
                question.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def reorderBadges(request):
    ''' This view is called by an ajax function to reorder badges'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        badgeIdsPositions = request.POST.getlist("badgeIdsPositions[]")
        for badgeIdPos in badgeIdsPositions:
            idPos = badgeIdPos.split("---")

            try:
                badge = BadgesInfo.objects.get(
                    badgeID=int(idPos[0]), courseID=currentCourse)
                badge.badgePosition = int(idPos[1])
                badge.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def reorderVCRules(request):
    ''' This view is called by an ajax function to reorder VCRules'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        ruleIdsPositions = request.POST.getlist("ruleIdsPositions[]")
        for ruleIdPos in ruleIdsPositions:
            idPos = ruleIdPos.split("---")

            try:
                rule = VirtualCurrencyCustomRuleInfo.objects.get(
                    vcRuleID=int(idPos[0]), courseID=currentCourse)
                rule.vcRulePosition = int(idPos[1])
                rule.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def reorderGroups(request):
    ''' This view is called by an ajax function to reorder Groups'''

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        groupIdsPositions = request.POST.getlist("groupIdsPositions[]")
        for groupIdPos in groupIdsPositions:
            idPos = groupIdPos.split("---")

            try:
                group = FlashCardGroupCourse.objects.get(
                    groupID=int(idPos[0]), courseID=currentCourse)
                group.groupPos = int(idPos[1])
                group.save()
            except:
                continue

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})
