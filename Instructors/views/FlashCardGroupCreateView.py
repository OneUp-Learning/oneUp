'''
Created on Oct 26, 2019

@author: cmickle118
'''
from Instructors.constants import default_time_str
from django.utils.timezone import make_naive
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import FlashCardGroup,FlashCardGroupCourse
from Instructors.views import utils
from Instructors.views.utils import localizedDate, utcDate
from oneUp.decorators import instructorsCheck
from datetime import datetime
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def groupCreateView(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
    
    if request.POST:
        
        # Check if groups with this name already exist
        groups = FlashCardGroup.objects.filter(groupName=request.POST['groupName'])
        if groups:
            group = groups[0]
        #sets group name
        else: 
            group = FlashCardGroup()           
            group.groupName = request.POST['groupName']                   
            group.save()
            
        #same as above, but with gID and cIDs
        cardGroups = FlashCardGroupCourse.objects.filter(groupID=group, courseID=currentCourse)
        if cardGroups:  
            cardGroup = cardGroups[0]                    
        else:
            cardGroup = FlashCardGroupCourse()
            cardGroup.groupID = group
            cardGroup.courseID = currentCourse
        
        default_date = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        if(request.POST['availabilityDate'] == ""):
            group.availabilityDate = default_date
        elif datetime.strptime(request.POST['availabilityDate'], "%m/%d/%Y %I:%M %p"):
            group.availabilityDate = localizedDate(request, request.POST['availabilityDate'], "%m/%d/%Y %I:%M %p")
        else:
            group.availabilityDate= default_date
        group.save()     
        cardGroup.groupPos = int(request.POST['groupPos'])
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
            context_dict['groupPos']= str(cg.groupPos)
            
            #handles the group date setting in the GET
            availabilityDate = localizedDate(request, str(make_naive(cg.availabilityDate.replace(microsecond=0))), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %I:%M %p")
            if cg.availabilityDate.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") != default_time_str:
                context_dict['availabilityDate']=availabilityDate
            else:
                context_dict['availabilityDate']= ""
                   
    return render(request,'Instructors/FlashCardGroupCreate.html', context_dict)

