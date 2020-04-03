'''
Created on Oct 23, 2019

@author: cmickle
'''
from django.shortcuts import render
from Instructors.models import FlashCardGroup,FlashCardGroupCourse,FlashCardToGroup,FlashCards
from Instructors.views import utils
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def groupListView(request):
  
    context_dict,currentCourse = utils.initialContextDict(request)   
           
    groupID = []      
    groupName = []
    groupPos = []
    all_cards_in_group=[]

    flash_ID=[]
    flash_Name=[]
    '''
    temp = 1
    if temp:
        unassigned_flashgroup = FlashCardGroup()
        unassigned_flashgroup.groupName = "Unassigned"
        unassigned_flashgroup.save()

        course_group = FlashCardGroupCourse()
        course_group.groupID = unassigned_flashgroup
        course_group.courseID= currentCourse
        course_group.save()
    '''

    cgroups = FlashCardGroupCourse.objects.filter(courseID=currentCourse)
    for cg in cgroups:
        gId = cg.groupID.groupID
        group = FlashCardGroup.objects.get(groupID=gId)
        groupID.append(gId)
        groupName.append(group.groupName)
        groupPos.append(cg.groupPos)

        cardGroup=FlashCardToGroup.objects.filter(groupID=gId)

        for card in cardGroup:
            fId=card.flashID.flashID
            flashcard=FlashCards.objects.get(flashID=fId)
            flash_Name.append(flashcard.flashName)
            flash_ID.append(fId)

    

    context_dict['groups']=utils.getGroupForCards(currentCourse,None)
    context_dict['groupsAuto'], context_dict['createdGroups']=utils.autoCompleteGroupsToJson(currentCourse)
    context_dict['group_range'] = sorted(list(zip(range(1,cgroups.count()+1),groupID,groupName,groupPos)),key=lambda tup: tup[3])
    context_dict['card_range'] = sorted(list(zip(range(1,cards.count()+1),flashID, flashName)),key=lambda tup: tup[2])
    return render(request,'Instructors/flashCardGroupList.html', context_dict)