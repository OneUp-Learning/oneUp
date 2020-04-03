'''
Created on Nov 5, 2019

@author: cmickle
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import FlashCards,FlashCardToGroup, FlashCardGroup
from oneUp.decorators import instructorsCheck
from Instructors.views import utils
from django.contrib.auth.decorators import login_required,user_passes_test
from _curses import flash

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def CreateFlashCard(request):
    context_dict,currentCourse = utils.initialContextDict(request) 
    if request.GET:
        if 'groupID' in request.GET and 'flashID' in request.GET:
            flashCard = FlashCards.objects.get(flashID=request.GET['flashID'])
            groupID = FlashCardGroup.objects.get(groupID=request.GET['groupID'])
            if FlashCardToGroup.objects.get(groupID=groupID, flashID=flashCard).exists():
                if request.POST:
                    flashCard.name= request.POST['cardName']
                    flashCard.front = request.POST['front']
                    flashCard.back = request.POST['back']
                    flashCard.save()
                
        elif 'groupID' in request.GET:
            if request.POST:
                flashCard_Group = FlashCardToGroup()
                flashCard_Group.groupID = FlashCardGroup.objects.get(groupID=request.GET['groupID'])
                flash_card = FlashCards()
                flash_card.name = request.POST['cardName']
                flash_card.front = request.POST['front']
                flash_card.back = request.POST['back']
                flash_card.save()
                flashCard_Group.flashID = flash_card
                flashCard_Group.save()
   # else:
        #return redirect('/oneUp/instructors/groupList.html')                     
    return render(request,'Instructors/CreateFlashCard.html', context_dict)

    
