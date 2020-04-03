'''
Created on Oct 23, 2019

@author: cmickle
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import FlashCards, FlashCardGroup, FlashCardGroupCourse, FlashCardToGroup
from Instructors.views import utils
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def CreateFlashCards(request):

    context_dict, currentCourse = utils.initialContextDict(request)

    if request.POST:
        print(request.POST['cardName'])
        flashCard=None
        try:
            flashCard=FlashCards.objects.get(flashID=request.POST['flashID'])
            flashCard.flashName= request.POST['cardName']
            flashCard.front = request.POST['front']
            flashCard.back = request.POST['back']
            flashCard.save()
        except:
            flashCard=FlashCards()
            flashCard.flashName = request.POST['cardName']
            flashCard.front = request.POST['front']
            flashCard.back = request.POST['back']
            flashCard.save()
        utils.saveGroupToCards(currentCourse,request.POST['groups'],flashCard)
        return redirect("/oneUp/instructors/groupList")

    #################################
    #  get request
    else:
        if 'groupID' in request.GET and 'flashID' in request.GET:
            flashCard = FlashCards.objects.get(pk=int(request.GET['flashID']))
            group = FlashCardGroup.objects.get(pk=int(request.GET['groupID']))
            if FlashCardToGroup.objects.get(groupID=groupID, flashID=flashCard).exists():
                    context_dict['groupName']=group.groupName
                    context_dict['cardName']=flashCard.name
                    context_dict['front']=flashCard.front
                    context_dict['back']=flashCard.back
    return render(request, 'Instructors/groupList.html', context_dict)
