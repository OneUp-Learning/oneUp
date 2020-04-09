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
  

    cgroups = FlashCardGroupCourse.objects.filter(courseID=currentCourse).order_by("groupPos")
    #FlashCardGroup.objects.all().delete()
    for cg in cgroups:
        gId = cg.groupID.groupID
        group = FlashCardGroup.objects.get(groupID=gId)
        groupID.append(gId)
        groupName.append(group.groupName)
        groupPos.append(cg.groupPos)

        cardGroup=FlashCardToGroup.objects.filter(groupID=gId)
        temp=[]
        for card in cardGroup:
            temp.append(card.flashID)
            print("****************************",card.flashID)
        all_cards_in_group.append(temp)

    

    context_dict['groups']=utils.getGroupForCards(currentCourse,None)
    context_dict['groupsAuto'], context_dict['createdGroups']=utils.autoCompleteGroupsToJson(currentCourse)
    context_dict['group_range'] = zip(range(1,cgroups.count()+1),groupID,groupName,groupPos,all_cards_in_group)
    
    return render(request,'Instructors/flashCardGroupList.html', context_dict)