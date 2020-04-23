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
		if('flashID' in request.POST):
			flashCardExists = FlashCards.objects.filter(flashID=request.POST['flashID']).exists()
			if(flashCardExists):
				flashCard = FlashCards.objects.filter(flashID=request.POST['flashID'])
		else: 
			flashCard = FlashCards()
		flashCard.flashName= request.POST['cardName']
		flashCard.front = request.POST['front']
		flashCard.back = request.POST['back']
		flashCard.save()
		
		if 'groupID' in request.GET:
			cardGroup=FlashCardToGroup.objects.get(groupID=request.GET(int(request.GET['universityID'])), flashID=flashCard)
		else:
			cardGroup = FlashCardToGroup()
		if 'course-groups' in request.POST:
			#get all groups assigned to card
			groups = request.POST.getlist('course-groups')
			#iterate through groups and save card to each selected group
			for id in groups:
				group = FlashCardGroup.objects.get(groupID=id)
				
				cardGroup.groupID=group
				cardGroup.flashID=flashCard
				print(cardGroup)
				cardGroup.save()
		#handles case of instructor not explicitly assigning a group
		else:
			unassigned_group = FlashCardToGroup()
			unassigned_group.flashID=flashCard
			unassigned_group.groupID=FlashCardGroupCourse.objects.get(groupID__groupName="Unassigned", courseID=currentCourse).groupID
			print(unassigned_group,"0000")
			unassigned_group.save()
		
		
		return redirect("/oneUp/instructors/groupList")

	if request.GET:
		context_dict['groups']=FlashCardGroupCourse.objects.exclude(groupID__groupName="Unassigned")

		if 'groupID' in request.GET and 'flashID' in request.GET:
			flashCard = FlashCards.objects.get(pk=int(request.GET['flashID']))
			group = FlashCardGroup.objects.get(pk=int(request.GET['groupID']))
			doesFlashCardToGroupExist = FlashCardToGroup.objects.filter(groupID=group, flashID=flashCard).exists()
			
			if doesFlashCardToGroupExist:
				flashToGroup = FlashCardToGroup.objects.get(groupID=group, flashID=flashCard)
				context_dict['groupName']=flashToGroup.groupID.groupName
				context_dict['cardName']=flashCard.flashName
				context_dict['front']=flashCard.front
				context_dict['back']=flashCard.back
	return render(request, '/oneUp/instructors/createFlashCard', context_dict)
