'''
Created on Oct 23, 2019

@author: cmickle
'''
from django.shortcuts import render
from Instructors.models import FlashCardGroup,FlashCardGroupCourse
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
           
    cgroups = FlashCardGroupCourse.objects.filter(courseID=currentCourse)
    for cg in cgroups:
        gId = cg.groupID.groupID
         
        group = FlashCardGroup.objects.get(groupID=gId)
        groupID.append(gId)
        groupName.append(group.groupName)
        groupPos.append(cg.groupPos)

    context_dict['group_range'] = sorted(list(zip(range(1,cgroups.count()+1),groupID,groupName,groupPos)),key=lambda tup: tup[3])

    return render(request,'Instructors/FlashCardGroupList.html', context_dict)