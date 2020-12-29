'''
Created on Oct 26, 2020

@author: cmickle
'''
from Instructors.constants import default_time_str
from django.utils.timezone import make_naive
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Students.models import Teams, StudentRegisteredCourses
from Instructors.views import utils
from Instructors.models import UploadedImages
from Instructors.views.utils import datetime_to_selected, str_datetime_to_local
from oneUp.decorators import instructorsCheck
from datetime import datetime
import glob
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def teamCreateView(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
   
        
    
    if request.POST:
        print("YYY")
        # Check if groups with this name already exist
        
        if 'teamID' in request.POST and request.POST['teamID'] != '':
            team = Teams.objects.get(teamID=request.POST['teamID'], courseID=currentCourse)
        else:
            
            team = Teams()
        team.teamName = request.POST['teamName']
        team.courseID=currentCourse
        if request.POST and len(request.FILES) != 0:  
            print("XXX",request.FILES['imagefile'])
            ##imageFile.name is the name of the file, we do not need a special field      
            imageFile = request.FILES['imagefile']
            imageObject = UploadedImages() 
            imageObject.imageFile = imageFile
            imageObject.imageCreator = request.user
            imageObject.save()
            team.avatarImage = imageObject.imageFile.url
            print(team.avatarImage,'ss')
        else:
            team.avatarImage = '/static/images/avatars/anonymous.png'
        team.save()
        print(team.avatarImage,'sss')
        
        
        return redirect('/oneUp/instructors/teamList.html')        
    #  get request
    else:
        
        if 'teamID' in request.GET:
            context_dict['teamID']=request.GET['teamID']
            team = Teams.objects.get(pk=int(request.GET['teamID']))
            context_dict['teamName'] = team.teamName
            context_dict['image'] = team.avatarImage
            
            


        

           
    return render(request,'Instructors/teamCreate.html', context_dict)


