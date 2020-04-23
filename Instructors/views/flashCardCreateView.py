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
		print("In post")
		edit = False
		if 'flashID' in request.POST:
			print("Editing")
			flashCard = FlashCards.objects.filter(flashID=request.POST['flashID']).first()
			edit = True
		else: 
			flashCard = FlashCards()
		flashCard.flashName= request.POST['cardName']
		flashCard.front = request.POST['front']
		flashCard.back = request.POST['back']
		flashCard.save()
		
		
		if 'cardGroups' in request.POST:
			print("In groups")
			#get all groups assigned to card
			groups = request.POST.getlist('cardGroups')

			flashcardsGroups = FlashCardToGroup.objects.filter(flashID=flashCard)
			newGroupsIDs = [int(group_id) for group_id in groups]
			existingIDs = [fc.groupID.pk for fc in flashcardsGroups]
			deletionIDs = [id for id in existingIDs if id not in newGroupsIDs]
			newIDs = [id for id in newGroupsIDs if id not in existingIDs]

			print(newGroupsIDs)
			print(existingIDs)
			print(deletionIDs)
			print(newIDs)

			for group_id in newIDs:
				flashcard=FlashCardToGroup()
				flashcard.flashID=flashCard
				flashcard.groupID=FlashCardGroup.objects.get(groupID=group_id)
				flashcard.save()
					
			for group_id in deletionIDs:
				flashcard=FlashCardToGroup.objects.get(groupID__groupID=group_id, flashID=flashCard)
				flashcard.delete()

		#handles case of instructor not explicitly assigning a group
		else:
			print("remove all groups")
			if edit:
				FlashCardToGroup.objects.filter(flashID=flashCard).delete()
			
			unassigned_group = FlashCardToGroup()
			unassigned_group.flashID=flashCard
			unassigned_group.groupID=FlashCardGroupCourse.objects.get(groupID__groupName="Unassigned", courseID=currentCourse).groupID
			print(unassigned_group,"0000")
			unassigned_group.save()
		
		
	return redirect("/oneUp/instructors/groupList")
