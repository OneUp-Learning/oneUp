'''
Created on Oct 26, 2019

@author: cmickle
'''
from Instructors.constants import default_time_str
from django.utils.timezone import make_naive
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import FlashCardGroup,FlashCardGroupCourse
from Instructors.views import utils
from Instructors.views.utils import datetime_to_selected, str_datetime_to_local
from oneUp.decorators import instructorsCheck
from datetime import datetime
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def groupCreateView(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
    
    if request.POST:
        
        # Check if groups with this name already exist
        
        if 'groupID' in request.POST and request.POST['groupID'] != '':
            group=FlashCardGroup.objects.get(groupID=request.POST['groupID'])
        else:
            group = FlashCardGroup()
            group.save()
        group.groupName = request.POST['groupName']
            
        #same as above, but with gID and cIDs
        if FlashCardGroupCourse.objects.filter(groupID=group.groupID, courseID=currentCourse).exists():
            cardGroup = FlashCardGroupCourse.objects.get(groupID=group.groupID, courseID=currentCourse)
        else:
            cardGroup = FlashCardGroupCourse()
            cardGroup.groupID = group
            cardGroup.courseID = currentCourse
        try:
            cardGroup.availabilityDate = str_datetime_to_local(request.POST['availabilityDate'])
            cardGroup.hasAvailabilityDate = True
            
        except ValueError:
            cardGroup.hasAvailabilityDate = False
        
        if cardGroup.hasAvailabilityDate:
                context_dict['availabilityDate'] = datetime_to_selected(cardGroup.availabilityDate)
        else:
                context_dict['availabilityDate'] = ""
       
        group.save()     
       # cardGroup.groupPos = int(request.POST['groupPos'])
        cardGroup.save()
        return redirect('/oneUp/instructors/groupList.html')        
    #  get request
    else:
        #Handles ID, Name, and Position
        if 'groupID' in request.GET:
            context_dict['groupID'] = request.GET['groupID']
            group = FlashCardGroup.objects.get(pk=int(request.GET['groupID']))
            context_dict['groupName']=group.groupName
            cg = FlashCardGroupCourse.objects.get(groupID=group,courseID=currentCourse)
          #  context_dict['groupPos']= str(cg.groupPos)
            group.save()

            if cg.hasAvailabilityDate:
                context_dict['availabilityDate'] = datetime_to_selected(cg.availabilityDate)
            else:
                context_dict['availabilityDate'] = ""
           
    return render(request,'Instructors/flashCardGroupCreate.html', context_dict)

