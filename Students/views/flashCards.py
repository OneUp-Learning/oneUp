'''
Created on April 21, 2020

@author: GGM
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from Students.views.utils import studentInitialContextDict, str2bool
from Students.models import studentFlashCards, Student
from Instructors.models import FlashCardGroupCourse, FlashCardGroup, FlashCardToGroup, FlashCards

from oneUp.decorators import instructorsCheck
import datetime

@login_required
def flashCardUsed(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    status = "failed"
    if request.POST:
        wasFlashIDSent = 'flashID' in request.POST
        wasGroupIDSent = 'groupID' in request.POST
        wasGotItSent = 'gotIt' in request.POST

        if wasFlashIDSent and wasGroupIDSent and wasGotItSent:
            student = Student.objects.get(user=request.user)

            flashID = request.POST['flashID']
            groupID = request.POST['groupID']
            gotIt = str2bool(request.POST['gotIt'])

            if(studentFlashCards.objects.filter(studentID=student, flashID=flashID).exists()):
                studentFlashCard = studentFlashCards.objects.get(studentID=student, flashID=flashID)
            else:
                studentFlashCard = studentFlashCards()
            studentFlashCard.studentID = student
            studentFlashCard.flashID = getFlashCardObjFromID(flashID)

            if(gotIt):
                if(studentFlashCard.cardBin < 3):
                    studentFlashCard.cardBin = studentFlashCard.cardBin + 1
                    
                studentFlashCard.timesCorrect = studentFlashCard.timesCorrect +1
                studentFlashCard.studyDate = getOptimumStudyTime(studentFlashCard.cardBin)
            if(not gotIt):
                studentFlashCard.cardBin = 0
                studentFlashCard.studyDate = datetime.datetime.now()
            studentFlashCard.timesSeen = studentFlashCard.timesSeen + 1
    
            studentFlashCard.save()
            status = "good"
            
    return JsonResponse({"status" : status})

def flashCards(request):
    #promtes cards up to the practice bin of zero if thier time has arrived
    #or is close to being here
    context_dict, current_course = studentInitialContextDict(request)
    if 'groupID' in request.GET:
        groupID = request.GET['groupID']
        context_dict['flash_range'] = getFlashCardsForPractice(groupID, request)
        context_dict['groupID'] = groupID
    return render(request,'Students/FlashCards.html',context_dict)

def flashCardsList(request):
    context_dict, current_course = studentInitialContextDict(request)
    context_dict['group_range'] = createGroupRange(current_course)
    return render(request,'Students/FlashCardsList.html',context_dict)

def createGroupRange(current_course):
    card_groups = FlashCardGroupCourse.objects.filter(courseID=current_course).order_by("groupPos")
    groupList = []
    for cg in card_groups:
        groupID = cg.groupID.groupID
        cardCount = len(FlashCardToGroup.objects.filter(groupID=groupID))
        group = FlashCardGroup.objects.get(groupID=groupID)
        groupList.append({'groupID': groupID, 'groupName': group.groupName , "cardCount": cardCount})
    return groupList

def cardShouldBeAdded(flashID, request):
    student = Student.objects.get(user=request.user)
    theyHaveFlashObject = studentFlashCards.objects.filter(studentID=student, flashID=flashID).exists()

    #if student doesnt have a flashID object relating to this add it
    if(not theyHaveFlashObject):
        return True

    if(theyHaveFlashObject):
        studentFlashCard = studentFlashCards.objects.get(studentID=student, flashID=flashID)

        #if they have one, and its bin is zero add it
        if(studentFlashCard.cardBin == 0):
            return True

        #if they have one and its date is due or behind us add it
        #if(studentFlashCard.studyDate <= datetime.datetime.now()):
        #    return True

def getFlashCardsForPractice(groupID, request):
    flash_cards_to_group = FlashCardToGroup.objects.filter(groupID=groupID)
    flash_cards = []
    for flash_card_to_group in flash_cards_to_group:
        flashCardID = flash_card_to_group.flashID.flashID
        flashCard = flash_card_to_group.flashID
        if(cardShouldBeAdded(flashCardID, request)):
            flash_cards.append({'question': flashCard.front, 'answer': flashCard.back,
        'flashName': flashCard.flashName, 'flashID': flashCardID})
    return flash_cards

def getFlashCardObjFromID(flashID):
    return FlashCards.objects.get(flashID=flashID)

def getOptimumStudyTime(time_bin):
    #two days later, a week, three weeks later.
    current_time = datetime.datetime.now() 
    if(time_bin == 1):
        delta = datetime.timedelta(days=2)
    if(time_bin == 2):
        delta = datetime.timedelta(days=7)
    if(time_bin == 3):
        delta = datetime.timedelta(days=21)
    future_time = current_time + delta
    return future_time