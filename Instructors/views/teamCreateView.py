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
from Instructors.views.utils import datetime_to_selected, str_datetime_to_local
from oneUp.decorators import instructorsCheck
from datetime import datetime
import glob
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def teamCreateView(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
   
        
    
    if request.POST:
        
        # Check if groups with this name already exist
        
        if 'teamID' in request.POST and request.POST['teamID'] != '':
            team = Teams.object.get(teamID=request.POST['teamID'])
        else:
            print(request.POST['avatar'],"XXXXXX")
            team = Teams()
            team.teamName = request.POST['teamName']
            team.courseID=currentCourse
            team.teamLeader =  StudentRegisteredCourses.objects.filter(courseID=currentCourse).first().studentID
            team.avatarImage = request.POST['avatar']
            team.save()



        
        return redirect('/oneUp/instructors/teamList.html')        
    #  get request
    else:
        
        if 'teamID' in request.GET:
            team = Teams.objects.get(pk=int(request.GET['teamID']))
            context_dict['team_name'] = team.teamName
            context_dict['avatarImage'] = team.avatarImage
            team.save()


        if Teams.objects.filter(courseID=currentCourse, teamName="x").exists():
            t = Teams.objects.get(courseID=currentCourse, teamName="x")
        else:
            t = Teams()
            t.courseID=currentCourse
            t.teamLeader = StudentRegisteredCourses.objects.filter(courseID=currentCourse).first().studentID
            t.teamName = "x"
            t.save()
        tID=t.teamID

        extractPaths(context_dict, currentCourse, tID)
        if Teams.objects.filter(courseID=currentCourse, teamName="x").exists():
            Teams.objects.get(courseID=currentCourse, teamName="x").delete()

           
    return render(request,'Instructors/teamCreate.html', context_dict)

def extractPaths(context_dict, currentCourse, tID): #function used to get the names from the file locaiton
    usedAvatars = []
    print("XXXXXXXXXXXXXXX")
    team = Teams.objects.get(courseID=currentCourse, teamID = tID)
    course_teams = Teams.objects.filter(courseID=currentCourse)
    for t in course_teams:
        usedAvatars.append(t.avatarImage)
    print(usedAvatars)
    
    avatarPath = []	
    for name in glob.glob('static/images/avatars/*'):
        name = name.replace("\\","/")
        namec = '/'+name
        if not namec in usedAvatars:
            avatarPath.append(name)
            print(name)	
    
    #Check to make sure the students avatar still exisit if not chagne to default
    checkIfAvatarExist(team)
        
    avatarPath.sort()
    context_dict["avatarPaths"] = zip(range(1,len(avatarPath)+1), avatarPath)

def checkIfAvatarExist(student):
    avatars = glob.glob('static/images/avatars/*')
    defaultAvatar = '/static/images/avatars/anonymous.png'
    studentAvatarPath = student.avatarImage
    studentAvatarPath = studentAvatarPath[1:]
    if studentAvatarPath in avatars:
        return student.avatarImage
    else:
        student.avatarImage = defaultAvatar #change the students avatar to the default
        student.save()

    return defaultAvatar 

