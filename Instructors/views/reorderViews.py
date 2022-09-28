'''
Created on February 27, 2020

@author: Omar
'''

from django.http import JsonResponse
from Instructors.models import CoursesTopics, Challenges, Activities, ActivitiesCategory, ChallengesQuestions,FlashCardGroupCourse, Trivia, TriviaQuestion
from Badges.models import BadgesInfo, VirtualCurrencyCustomRuleInfo
import json
import logging

from django.http import JsonResponse

from Badges.models import BadgesInfo, VirtualCurrencyCustomRuleInfo
from Instructors.models import (Activities, ActivitiesCategory, Challenges,
                                ChallengesQuestions, ChallengesTopics,
                                CoursesTopics, Topics)
from Instructors.views import utils

# Get an instance of a logger
logger = logging.getLogger(__name__)

# def reorderTopics(request):
#     ''' This view is called by an ajax function to reorder topics'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     print("reorderTopics")
#     print(request.POST)
#     if request.POST:
#         topicIdsPositions = request.POST.getlist("topicIdsPositions[]")
#         print("topicIdsPositions")
#         print(topicIdsPositions)

#         for topicIdPos in topicIdsPositions:
#             idPos = topicIdPos.split("---")
#             print(idPos)
#             try:
#                 courseTopic = CoursesTopics.objects.get(
#                     topicID__topicID=int(idPos[0]), courseID=currentCourse)
#                 courseTopic.topicPos = int(idPos[1])
#                 courseTopic.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})


# def reorderChalls(request):
#     ''' This view is called by an ajax function to reorder challenges'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     if request.POST:
#         challIdsPositions = request.POST.getlist("challIdsPositions[]")

#         for challIdPos in challIdsPositions:
#             idPos = challIdPos.split("---")
#             try:
#                 chall = Challenges.objects.get(
#                     challengeID=int(idPos[0]), courseID=currentCourse)
#                 chall.challengePosition = int(idPos[1])
#                 chall.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})


# def reorderCategories(request):
#     ''' This view is called by an ajax function to reorder categories'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     if request.POST:
#         catIdsPositions = request.POST.getlist("catIdsPositions[]")
#         for catdPos in catIdsPositions:
#             idPos = catdPos.split("---")

#             try:
#                 cat = ActivitiesCategory.objects.get(
#                     categoryID=int(idPos[0]), courseID=currentCourse)
#                 cat.catPosition = int(idPos[1])
#                 cat.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})


# def reorderActivities(request):
#     ''' This view is called by an ajax function to reorder activities'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     if request.POST:
#         activityIdsPositions = request.POST.getlist("activityIdsPositions[]")
#         for activityIdPos in activityIdsPositions:
#             idPos = activityIdPos.split("---")

#             try:
#                 activity = Activities.objects.get(
#                     activityID=int(idPos[0]), courseID=currentCourse)
#                 activity.activityPosition = int(idPos[1])
#                 activity.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})


# def reorderQuestions(request):
#     ''' This view is called by an ajax function to reorder questions'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     if request.POST:
#         questionIdsPositions = request.POST.getlist("questionIdsPositions[]")
#         for questionIdPos in questionIdsPositions:
#             idPos = questionIdPos.split("---")

#             try:
#                 question = ChallengesQuestions.objects.get(
#                     questionID__questionID=int(idPos[0]), challengeID__courseID=currentCourse)
#                 question.questionPosition = int(idPos[1])
#                 question.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})


# def reorderBadges(request):
#     ''' This view is called by an ajax function to reorder badges'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     if request.POST:
#         badgeIdsPositions = request.POST.getlist("badgeIdsPositions[]")
#         for badgeIdPos in badgeIdsPositions:
#             idPos = badgeIdPos.split("---")

#             try:
#                 badge = BadgesInfo.objects.get(
#                     badgeID=int(idPos[0]), courseID=currentCourse)
#                 badge.badgePosition = int(idPos[1])
#                 badge.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})


# def reorderVCRules(request):
#     ''' This view is called by an ajax function to reorder VCRules'''

#     context_dict, currentCourse = utils.initialContextDict(request)

#     if request.POST:
#         ruleIdsPositions = request.POST.getlist("ruleIdsPositions[]")
#         for ruleIdPos in ruleIdsPositions:
#             idPos = ruleIdPos.split("---")

#             try:
#                 rule = VirtualCurrencyCustomRuleInfo.objects.get(
#                     vcRuleID=int(idPos[0]), courseID=currentCourse)
#                 rule.vcRulePosition = int(idPos[1])
#                 rule.save()
#             except:
#                 continue

#         return JsonResponse({"success": True})
#     return JsonResponse({"success": False})

def receive_item_in_section(request):
    ''' This will move a item (challenge or activity) to a new section (topic or category)
        request method must be POST and should include:
        (str) type :
            challenge | activity
        (int) item-id:
            (Challenges.id | Activities.id)
        (int) section-id:
            (Topics.id | ActivitiesCategory.id)
    '''
    if request.method == "POST":
        json_data = json.loads(request.body)
        context_dict, current_course = utils.initialContextDict(request)
        item_type = json_data['type']
        item_id = int(json_data['item-id'])
        section_id = int(json_data['section-id'])

        if item_type == 'challenge':
            try:
                challenge = ChallengesTopics.objects.get(
                    challengeID__pk=item_id, challengeID__courseID=current_course)
                challenge.topicID = Topics.objects.get(pk=section_id)
                challenge.save()
            except:
                logger.warn(f"Couldn't add challenge {item_id} to topic {section_id}")
        elif item_type == 'activity':
            try:
                activity = Activities.objects.get(
                    activityID=item_id, courseID=current_course)
                activity.category = ActivitiesCategory.objects.get(
                    pk=section_id, courseID=current_course)
                activity.save()
            except:
                logger.warn(f"Couldn't add activity {item_id} to category {section_id}")

        return JsonResponse({"success": True, "message": "Received item in section"})

    return JsonResponse({"success": False, "message": "Incorrect method type"})

def reorder_list(request):
    ''' This will reorder a list of objects of a type
        request method must be POST and should include:
        (str) type :
            topic | challenge | activity | activity-category | question | badge | vc-rule
        (list) positions:
            [ {'id': int, 'value': int}, ..., {'id': int, 'value': int} ]
    '''
    if request.method == "POST":
        json_data = json.loads(request.body)
        context_dict, current_course = utils.initialContextDict(request)
        positions = json_data['positions']
        item_type = json_data['type']
        for item in positions:
            if item_type == 'topic':
                try:
                    course_topic = CoursesTopics.objects.get(
                        topicID__topicID=int(item['id']), courseID=current_course)
                    course_topic.topicPos = int(item['value'])
                    course_topic.save()
                except:
                    continue
            elif item_type == 'challenge':
                try:
                    challenge = Challenges.objects.get(
                        challengeID=int(item['id']), courseID=current_course)
                    challenge.challengePosition = int(item['value'])
                    challenge.save()
                except:
                    continue
            elif item_type == 'activity':
                try:
                    activity = Activities.objects.get(
                        activityID=int(item['id']), courseID=current_course)
                    activity.activityPosition = int(item['value'])
                    activity.save()
                except:
                    continue

            elif item_type == 'activity-category':
                try:
                    category = ActivitiesCategory.objects.get(
                        categoryID=int(item['id']), courseID=current_course)
                    category.catPosition = int(item['value'])
                    category.save()
                except:
                    continue
            
            elif item_type == 'question':
                try:
                    question = ChallengesQuestions.objects.get(
                        questionID__questionID=int(item['id']), challengeID__courseID=current_course)
                    question.questionPosition = int(item['value'])
                    question.save()
                except:
                    continue

            elif item_type == 'badge':
                try:
                    badge = BadgesInfo.objects.get(
                        badgeID=int(item['id']), courseID=current_course)
                    badge.badgePosition = int(item['value'])
                    badge.save()
                except:
                    continue

            elif item_type == 'vc-rule':
                try:
                    rule = VirtualCurrencyCustomRuleInfo.objects.get(
                        vcRuleID=int(item['id']), courseID=current_course)
                    rule.vcRulePosition = int(item['value'])
                    rule.save()
                except:
                    continue
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Incorrect method type"})
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

def reorderTriviaQuestions(request):
    ''' This view is called by an ajax function to reorder Trivia Questions'''
    context_dict, currentCourse = utils.initialContextDict(request)

    if request.method == "POST":
        json_data = json.loads(request.body)
        if 'triviaID' in json_data:
            triviaID = json_data['triviaID']
            
            trivia = Trivia.objects.get(triviaID=triviaID, courseID=currentCourse)
            
            if 'questionIdsPositions' in json_data:
                questionIdsPositions = json_data['questionIdsPositions']
                for questionIdPos in questionIdsPositions:
                    try:
                        question = TriviaQuestion.objects.get(
                            triviaID=trivia, questionID=int(questionIdPos['id']))
                        question.questionPosition = int(questionIdPos['value'])
                        question.save()
                    except:
                        continue
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})