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
    if not FlashCardGroup.objects.filter(groupName="Unassigned").exists():
        unassigned_flashgroup = FlashCardGroup()
        unassigned_flashgroup.groupName = "Unassigned"
        unassigned_flashgroup.save()
        course_group = FlashCardGroupCourse()
        course_group.groupID = unassigned_flashgroup
        course_group.courseID = currentCourse
        course_group.save()

    cgroups = FlashCardGroupCourse.objects.filter(courseID=currentCourse).order_by("groupPos")
    #FlashCardGroup.objects.all().delete()
    for cg in cgroups:
        gId = cg.groupID.groupID
        group = FlashCardGroup.objects.get(groupID=gId)
        groupID.append(gId)
        groupName.append(group.groupName)
        groupPos.append(cg.groupPos)
        #print(group.groupName)
        cardGroup=FlashCardToGroup.objects.filter(groupID=gId)
        temp=[]
        all_groups_of_card=[]
        for card in cardGroup:
            temp.append(card.flashID)
            all_groups_of_card.append([{"name":group.groupID.groupName, "id" : group.groupID.pk }for group in FlashCardToGroup.objects.filter(flashID=card.flashID)])
            #print("****************************",card.flashID)
        all_cards_in_group.append(zip(range(len(temp)),temp, all_groups_of_card))

    #context entry for displaying groups in modal create
    groups=[ {"name":group.groupID.groupName, "id" : group.groupID.pk } for group in FlashCardGroupCourse.objects.filter(courseID=currentCourse).exclude( groupID__groupName="Unassigned")]
    context_dict['create_groups']=groups

    context_dict['groups']=utils.getGroupForCards(currentCourse,None)
    #context_dict['groupsAuto'], context_dict['createdGroups']=utils.autoCompleteGroupsToJson(currentCourse)
    context_dict['group_range'] = zip(range(cgroups.count()),groupID,groupName,groupPos,all_cards_in_group)
    
    return render(request,'Instructors/flashCardGroupList.html', context_dict)