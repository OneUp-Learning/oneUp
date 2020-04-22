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
		flashcardGroups = request.POST.getlist('courseGroups')
		
		groups=[FlashCardGroup.objects.get(groupID=id) for id in flashcardGroups]
		'''

		context_dict['universities'] = Universities.objects.all()
		nonQualifiedCourses = [
		universityCourse.courseID for universityCourse in UniversityCourses.objects.all()]
		context_dict['qualified_courses'] = [
		course for course in Courses.objects.all() if not course in nonQualifiedCourses]
		'''

		unassigned_group = FlashCardToGroup()
		unassigned_group.flashID=flashID
		unassigned_group.groupID = FlashCardGroup.objects.get(groupName="Unassigned")
		unassigned_group.save()
		#utils.saveGroupToCards(currentCourse,request.POST['groups'],flashCard)
		return redirect("/oneUp/instructors/groupList")

	if request.GET:
		context_dict['groups']=FlashCardGroupCourse.objects.exclude(groupID__groupName="Unassigned")

		if 'groupID' in request.GET and 'flashID' in request.GET:
			flashCard = FlashCards.objects.get(pk=int(request.GET['flashID']))
			group = FlashCardGroup.objects.get(pk=int(request.GET['groupID']))
			doesFlashCardToGroupExist = FlashCardToGroup.objects.filter(groupID=group.groupID, flashID=flashCard).exists()
			
			if doesFlashCardToGroupExist:
				flashToGroup = FlashCardToGroup.objects.get(groupID=group.groupID, flashID=flashCard)
				context_dict['groupName']=flashToGroup.groupID.groupName
				context_dict['cardName']=flashCard.flashName
				context_dict['front']=flashCard.front
				context_dict['back']=flashCard.back
	return render(request, '/oneUp/instructors/createFlashCard', context_dict)
