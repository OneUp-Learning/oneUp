'''
Created on April 20, 2020

@author: GGM
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from Students.views.utils import studentInitialContextDict, str2bool
from Students.models import studentFlashCards, Student
from Instructors.models import FlashCardGroupCourse, FlashCardGroup, FlashCardToGroup, FlashCards
from Instructors.views.utils import datetime_to_local
from oneUp.decorators import instructorsCheck
from Badges.events import register_event
from Badges.enums import Event
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

            register_event(Event.submitFlashCard,request,student,int(flashID))

            if 'nextflashID' in request.POST:
                register_event(Event.viewFlashCard,request,student,int(request.POST['nextflashID']))
            if(studentFlashCards.objects.filter(studentID=student, flashID=flashID).exists()):
                studentFlashCard = studentFlashCards.objects.get(studentID=student, flashID=flashID)
            else:
                studentFlashCard = studentFlashCards()
            studentFlashCard.studentID = student
            print("XXX")
            studentFlashCard.flashID = getFlashCardObjFromID(flashID)
            
            if(gotIt):
                if(studentFlashCard.cardBin < 3):
                    studentFlashCard.cardBin = studentFlashCard.cardBin + 1
                    
                studentFlashCard.timesCorrect = studentFlashCard.timesCorrect +1
                studentFlashCard.studyDate = getOptimumStudyTime(studentFlashCard.cardBin)
            if(not gotIt):
                studentFlashCard.cardBin = 0
                studentFlashCard.studyDate = datetime_to_local(datetime.datetime.now())
            studentFlashCard.timesSeen = studentFlashCard.timesSeen + 1
    
            studentFlashCard.save()
           
            status = "good"
            
    return JsonResponse({"status" : status})

def flashCards(request):
    #promtes cards up to the practice bin of zero if thier time has arrived
    #or is close to being here
    context_dict, current_course = studentInitialContextDict(request)
    student = Student.objects.get(user=request.user)
    if 'groupID' in request.GET:
        groupID=[]
        groupID.append(request.GET['groupID'])
        print(len(groupID))
        if groupID[0] == "ALL":
            context_dict['flash_range'] = getFlashCards(groupID, request, True)
        else:
            context_dict['flash_range'] = getFlashCards(groupID, request)
            print("###",groupID)
    if 'study-checkboxes' in request.POST:
        listOfRequestedCardsGroups = []
        requested_groups = request.POST.getlist('study-checkboxes')
        print(requested_groups,"LLL")
        print(len(requested_groups))
       
        print("$$$$",requested_groups)
        context_dict['flash_range'] = getFlashCards(requested_groups, request)
    register_event(Event.viewFlashCard, request, student, context_dict['flash_range'][0]['flashID'])
    return render(request,'Students/FlashCards.html',context_dict)

def flashCardsList(request):
    context_dict, current_course = studentInitialContextDict(request)
    context_dict['group_range'] = createGroupRange(current_course)
    return render(request,'Students/FlashCardsList.html',context_dict)

def getOptimumStudyTime(time_bin):
    #two days later, a week, three weeks later.
    current_time = datetime_to_local(datetime.datetime.now())
    if(time_bin == 1):
        delta = datetime.timedelta(days=2)
    if(time_bin == 2):
        delta = datetime.timedelta(days=7)
    if(time_bin == 3):
        delta = datetime.timedelta(days=21)
    future_time = current_time + delta
    return future_time

def createGroupRange(current_course):
    card_groups = FlashCardGroupCourse.objects.filter(courseID=current_course).order_by("groupPos")
    groupList = []
    for cg in card_groups:
        groupID = cg.groupID.groupID
        cardCount = len(FlashCardToGroup.objects.filter(groupID=groupID))
        group = FlashCardGroup.objects.get(groupID=groupID)
        groupList.append({'groupID': groupID, 'groupName': group.groupName , "cardCount": cardCount})
    return groupList

def getFlashCardObjFromID(flashID):
    return FlashCards.objects.get(flashID=flashID)

def getFlashCards(groupIDs, request, all_cards=False):
    #get all the cards in the course no exceptions
    if(all_cards):        
        context_dict, currentCourse = studentInitialContextDict(request)
        card_groups = FlashCardGroupCourse.objects.filter(courseID=currentCourse).exclude(groupID_id__groupName="Unassigned")

        groupIDs = []
        for card_group in card_groups:
            groupIDs.extend(list(FlashCardToGroup.objects.filter(groupID=card_group.groupID)))
        return getCardsFromGroup(groupIDs,request, True)
    
    #get the the flash cards for a predetermined list of groups
    if(len(groupIDs)> 1):
        card_groups = []
        for groupID in groupIDs:
            card_groups.extend(list(FlashCardToGroup.objects.filter(groupID=groupID)))
        print("^^^^^^^^^^^",groupIDs[0])
        return getCardsFromGroup(card_groups, request)
    
    #singular card group
    if(len(groupIDs) == 1):
        card_group = list(FlashCardToGroup.objects.filter(groupID=groupIDs[0]))
        print("************",card_group)
        return getCardsFromGroup(card_group, request)

def getCardsFromGroup(flashCards, request, all_cards=False):
    flash_cards = []
    for flashCardToGroup in flashCards:
        flash_card = flashCardToGroup.flashID
        groupID = flashCardToGroup.groupID.groupID

        #all cards is used to overide the filtering for the case of all cards
        if(cardShouldBeAdded(flash_card.flashID, request) or all_cards):
            flash_cards.append({'question': flash_card.front, 'answer': flash_card.back,
        'flashName': flash_card.flashName, 'flashID': flash_card.flashID, 'groupID': groupID})
    return flash_cards

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
        if(datetime_to_local(studentFlashCard.studyDate) <= datetime_to_local(datetime.datetime.now())):
           return True
    return False