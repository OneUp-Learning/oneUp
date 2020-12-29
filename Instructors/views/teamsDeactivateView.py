'''
Created on Oct 26, 2020

@author: cmickle
'''
from Instructors.constants import default_time_str
from django.utils.timezone import make_naive
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Students.models import Teams, StudentRegisteredCourses, TeamStudents
from Instructors.views import utils
from Instructors.views.utils import datetime_to_selected, str_datetime_to_local
from oneUp.decorators import instructorsCheck
from datetime import datetime
import glob
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def deactivateTeams(request):
    context_dict,currentCourse = utils.initialContextDict(request)

    teams = Teams.objects.filter(courseID=currentCourse, activeTeam = True).exclude(teamName = 'Unassigned Students')

    for team in teams:
        team.activeTeam = False
        team_students = TeamStudents.objects.filter(teamID=team)

        for student in team_students:
            student.activeMember = False
            student.save()
        team.save()

    return redirect("/oneUp/instructors/teamList")