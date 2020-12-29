'''
Created on Oct 23, 2019

@author: cmickle
'''
import pprint
import random
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from Students.models import Teams, TeamStudents, StudentRegisteredCourses
from Instructors.views import utils
from Badges.models import CourseConfigParams
from oneUp.decorators import instructorsCheck
from Students.views.avatarView import checkIfAvatarExist
pp = pprint.PrettyPrinter(indent=4)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def pastTeams(request):
    context_dict,currentCourse = utils.initialContextDict(request)

    
    #get information on all the teams for display
    team_ID = []
    team_name = []
    team_avatar = []
    
    students_in_team = []
    teams = Teams.objects.filter(courseID=currentCourse, activeTeam=False)

    for team in teams:
        team_ID.append(team.teamID)
        team_name.append(team.teamName)
        team_avatar.append(team.avatarImage)

        team_students = TeamStudents.objects.filter(teamID=team, activeMember=False)
        temp = []
        enroll_mode = []
        for ts in team_students:
            temp.append(ts.studentID)
            enroll_mode.append(ts.modeOfEnrollment)
        if team.teamLeader in temp:
            temp.remove(team.teamLeader)
            temp.insert(0, team.teamLeader)

        students_in_team.append(list(zip(temp, enroll_mode)))
        
    if teams:
        team_ID = team_ID[1:] + [team_ID[0]]
        team_name = team_name[1:] + [team_name[0]]
        team_avatar = team_avatar[1:] + [team_avatar[0]]
        
        students_in_team = students_in_team[1:] + [students_in_team[0]]
        

    
    context_dict['teams_range'] = list(zip(range(teams.count()), team_ID, team_name, team_avatar, students_in_team))
    context_dict['group'] = (1, 3, 4, 6)
    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
    
    context_dict['lockInDate'] = ccparams.teamsLockInDeadline
    context_dict['selfAssignment'] = ccparams.selfAssignment
   
   

    return render(request,'Instructors/pastTeams.html', context_dict)