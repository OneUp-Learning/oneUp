'''
Created on Oct 23, 2019

@author: cmickle
'''
import pprint

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from Students.models import Teams, TeamStudents, StudentRegisteredCourses
from Instructors.views import utils
from oneUp.decorators import instructorsCheck
from Students.views.avatarView import checkIfAvatarExist
pp = pprint.PrettyPrinter(indent=4)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def teamListView(request):
    context_dict,currentCourse = utils.initialContextDict(request)

    #create category that will contain the students without a team
    if not Teams.objects.filter(courseID=currentCourse, teamName="Unassigned Students").exists():
        unassigned_team = Teams()
        unassigned_team.courseID=currentCourse
        unassigned_team.teamName = "Unassigned Students"
        unassigned_team.teamLeader = StudentRegisteredCourses.objects.filter(courseID=currentCourse)[0].studentID
        unassigned_team.save()
    else:
        unassigned_team = Teams.objects.get(teamName="Unassigned Students")
        
    unassigned_students = getUnassignedStudents(unassigned_team,currentCourse)
    if unassigned_students:
        addStudentsToTeam(unassigned_team,unassigned_students,currentCourse)
    #get information on all the teams for display
    team_ID = []
    team_name = []
    team_avatar = []
    students_in_team = []
    teams = Teams.objects.filter(courseID=currentCourse)

    for team in teams:
        team_ID.append(team.teamID)
        team_name.append(team.teamName)
        team_avatar.append(checkIfAvatarExist(team))

        team_students = TeamStudents.objects.filter(teamID=team)
        temp = []
        for ts in team_students:
            temp.append(ts.studentID)
        students_in_team.append(temp)
       
    team_ID = team_ID[1:] + [team_ID[0]]
    team_name = team_name[1:] + [team_name[0]]
    team_avatar = team_avatar[1:] + [team_avatar[0]]
    print(team_students)
    students_in_team = students_in_team[1:] + [students_in_team[0]]
    context_dict['teams_range'] = list(zip(range(teams.count()), team_ID, team_name, team_avatar, students_in_team))
    context_dict['group'] = (1, 3, 4, 6)
   
   

    return render(request,'Instructors/teamList.html', context_dict)
#function adds students to a team
def addStudentsToTeam(team,students,course):
    for student in students:
        st = TeamStudents()
        st.teamID = team
        st.studentID = student
        st.save()

   

#function finds students without an assigned team and assigns them all to 'unassigned team'
def getUnassignedStudents(unassigned_team, course):
    #get students in course
    students = StudentRegisteredCourses.objects.filter(courseID=course)
    studentIDs = [student.studentID for student in students]

    #get students that aren't in a team
    unassigned_students = []
    [unassigned_students.append(ID) for ID in studentIDs if not TeamStudents.objects.filter(studentID=ID).exists() and not ID.isTestStudent]
    if unassigned_students:
        unassigned_team.teamLeader = unassigned_students[0]
        unassigned_team.save()
    return unassigned_students
    

