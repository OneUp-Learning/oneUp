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
def CreateNTeams(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
    teams = Teams.objects.filter(courseID=currentCourse)
    total_teams = teams.count()-1
    if 'numberOfTeams' in request.POST and int(request.POST['numberOfTeams']) != 0:
        for i in range(int(request.POST['numberOfTeams'])):
            team = Teams()
            team.courseID=currentCourse
            if Teams.objects.filter(courseID=currentCourse, teamName="Team {}".format(i+1+total_teams)).exists():
                for j in range(i+1+total_teams, i+1+total_teams*2):
                    if Teams.objects.filter(courseID=currentCourse, teamName="Team {}".format(j)).exists():
                        continue
                    else:
                        team.teamName = "Team {}".format(j)
                        break
            else:
                team.teamName = "Team {}".format(i+1+total_teams)
            team.teamLeader = StudentRegisteredCourses.objects.filter(courseID=currentCourse)[0].studentID
            team.save()    
        
    return redirect("/oneUp/instructors/teamList")