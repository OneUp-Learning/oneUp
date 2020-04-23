'''
Created on April 21, 2020

@author: GGM
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from Students.views.utils import studentInitialContextDict
from Instructors.models import FlashCardGroupCourse, FlashCardGroup, FlashCardToGroup
from Students.models import studentFlashCards
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
        context_dict['groupID'] = groupID
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
        flash_cards.append({'question': front, 'answer': back, 'flashName': flashName, 'flashID': flashID.flashID})
    return flash_cards

def getAllCardsForFullStudy():
    True
def getCardsForStudentForLowestBin():
    True
@login_required
def flashCardUsed(request):
    ##this is used to promote a card up a bin
    
    context_dict, currentCourse = studentInitialContextDict(request)

    hints = {}
    response = {}
    #dict['hintsUsed'] = {}

    # studentFlashCards(models.Model):
    # studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    # flashID = models.ForeignKey(FlashCards,on_delete=models.CASCADE, verbose_name="the flash card",db_index=True)
    # studyDate = models.DateTimeField(default=now, verbose_name="the ideal date the flash card should reappear", db_index=True)
    # cardBin = models.IntegerField(default=0, verbose_name="priority containers for flash cards", db_index=True)
    # timesSeen = models.IntegerField(default=0, verbose_name="times the student has seen the card")
    # timesCorrect

    if request.POST:
        if 'flashID' in request.POST and 'groupID' in request.POST:
            if(studentFlashCards.objects.filter(studentID=request.user).exists()):
                studentFlashCard = studentFlashCards.objects.get(user=request.user)
            else:
                studentFlashCard = studentFlashCards()

            # if('gotIt' in request.POST)
            return JsonResponse( 
                {
                "hintID" : True ,
                "hint": True
                }
            )