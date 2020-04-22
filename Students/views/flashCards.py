'''
Created on April 21, 2020

@author: GGM
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from Students.views.utils import studentInitialContextDict
from Instructors.models import FlashCardGroupCourse, FlashCardGroup, FlashCardToGroup
from oneUp.decorators import instructorsCheck
 
def flashCardsList(request):
    context_dict, current_course = studentInitialContextDict(request)
    context_dict['group_range'] = createGroupDictionary(current_course)
    return render(request,'Students/FlashCardsList.html',context_dict)

def flashCards(request):
    context_dict, current_course = studentInitialContextDict(request)
    if 'groupID' in request.GET:
        groupID = request.GET['groupID']
        context_dict['flash_range'] = getFlashCardsForPractice(groupID)
        context_dict['group_name'] = FlashCardGroup.objects.get(groupID=groupID).groupName
    return render(request,'Students/FlashCards.html',context_dict)

def createGroupDictionary(current_course):
    card_groups = FlashCardGroupCourse.objects.filter(courseID=current_course).order_by("groupPos")
    groupList = []
    for cg in card_groups:
        groupID = cg.groupID.groupID
        cardCount = len(FlashCardToGroup.objects.filter(groupID=groupID))
        group = FlashCardGroup.objects.get(groupID=groupID)
        groupList.append({'groupID': groupID, 'groupName': group.groupName , "cardCount": cardCount})
    return groupList

def getFlashCardsForPractice(groupID):
    flash_cards_to_group = FlashCardToGroup.objects.filter(groupID=groupID)
    flash_cards = []
    for flash_Card in flash_cards_to_group:
        flashID = flash_Card.flashID
        flashName = flash_Card.flashID.flashName
        front = flash_Card.flashID.front
        back = flash_Card.flashID.back
        flash_cards.append({'question': front, 'answer': back, 'flashName': flashName, 'flashID': flashID})
    return flash_cards