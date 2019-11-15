'''
Created on Nov 5, 2019

@author: cmickle
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import FlashCards,FlashCardToGroup
from oneUp.decorators import instructorsCheck
from Instructors.views import utils
from django.contrib.auth.decorators import login_required,user_passes_test

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def CreateFlashCard(request):
    context_dict,currentCourse = utils.initialContextDict(request) 
    if request.POST:
        
        if 'flashID' in request.POST and request.POST['flashID'] != '':
            card=FlashCards.objects.get(groupID=request.POST['flashID'])
        else:
            card = FlashCards()
            card.save()
        card.front= request.POST['front']
        card.back = request.POST['back']
            
       
        if FlashCards.objects.filter(flashID=card.flashID).exists():
            cardGroup = FlashCardToGroup.objects.get(flashID=card.flashID, groupID=card.groupID)
        else:
            cardGroup = FlashCardToGroup
            cardGroup.groupID = card
            cardGroup.courseID = currentCourse
        card.save()     
        cardGroup.save()
        return redirect('/oneUp/instructors/groupList.html')        
    #  get request
    else:
        if 'flashID' in request.GET:
            context_dict['flashID'] = request.GET['flashID']
            card = FlashCards.objects.get(pk=int(request.GET['flashID']))
            context_dict['front']=card.front
            context_dict['back']=card.back
            card.save()
                   
    return render(request,'Instructors/CreateFlashCard.html', context_dict)

    
