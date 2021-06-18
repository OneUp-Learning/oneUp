'''
Created on Jun 15, 2021
@author: Charles
'''
from django.shortcuts import render
from Badges.models import PlayerType
from Instructors.constants import  unspecified_topic_name
from Instructors.views import utils
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def playerTypeListView(request):
  
    context_dict,currentCourse = utils.initialContextDict(request)   
           
    playerTypeID = []      
    playerTypeName = []
    playerTypes = PlayerType.objects.filter(course=currentCourse)
    for pt in playerTypes:
        pId = pt.id
        print(pt)
         
        
        playerTypeID.append(pId)
        playerTypeName.append(pt.name)


    context_dict['pt_range'] = sorted(list(zip(range(1,playerTypes.count()+1),playerTypeID,playerTypeName)),key=lambda tup: tup[1])

    return render(request,'Instructors/PlayerTypeList.html', context_dict)
