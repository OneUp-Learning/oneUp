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
from Instructors.views.utils import current_localtime
from Badges.models import CourseConfigParams
from oneUp.decorators import instructorsCheck
from Students.views.avatarView import checkIfAvatarExist
from Students.views.utils import studentInitialContextDict

pp = pprint.PrettyPrinter(indent=4)

@login_required
def teamList(request):
    context_dict,currentCourse = studentInitialContextDict(request)

    #create category that will contain the students without a team
    if not Teams.objects.filter(courseID=currentCourse, teamName="Unassigned Students").exists():
        unassigned_team = Teams()
        unassigned_team.courseID=currentCourse
        unassigned_team.teamName = "Unassigned Students"
        unassigned_team.teamLeader = StudentRegisteredCourses.objects.filter(courseID=currentCourse)[0].studentID
        unassigned_team.save()
    else:
        unassigned_team = Teams.objects.get(courseID=currentCourse, teamName="Unassigned Students")
        
    unassigned_students = getUnassignedStudents(unassigned_team,currentCourse)
    if unassigned_students:
        addStudentsToTeam(unassigned_team,unassigned_students,currentCourse)
    #get information on all the teams for display
    team_ID = []
    team_name = []
    team_avatar = []
    #Does team have the max number students allowed?
    team_available = []
    students_in_team = []
    teams = Teams.objects.filter(courseID=currentCourse, activeTeam=True)

    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)

    for team in teams:
        team_ID.append(team.teamID)
        team_name.append(team.teamName)
        team_avatar.append(team.avatarImage)

        team_students = TeamStudents.objects.filter(teamID=team)
        if ccparams.maxNumberOfTeamStudents > len(team_students):
            team_available.append(True)
        else: 
            team_available.append(False)
        temp = []
        enroll_mode = []
        for ts in team_students:
            temp.append(ts.studentID)
            print(ts.studentID)
            enroll_mode.append(ts.modeOfEnrollment)

        if team.teamLeader in temp:
            index = temp.index(team.teamLeader)
            print("Index: ", index)
            temp.remove(team.teamLeader)
            temp.insert(0, team.teamLeader)
            #reorder enrollment mode
            em = enroll_mode[index]
            enroll_mode.remove(em)
            enroll_mode.insert(0, em)
            print("EMI", em)
        students_in_team.append(list(zip(temp, enroll_mode)))
        
    if teams:
        #Put unassigned students at bottom
        team_ID = team_ID[1:] + [team_ID[0]]
        team_name = team_name[1:] + [team_name[0]]
        team_avatar = team_avatar[1:] + [team_avatar[0]]
        team_available = team_available[1:] + [team_available[0]]
        students_in_team = students_in_team[1:] + [students_in_team[0]]
        

    
    context_dict['teams_range'] = list(zip(range(teams.count()), team_ID, team_name, team_avatar,team_available, students_in_team))
    context_dict['group'] = (1, 3, 4, 6)
    
    context_dict['lockInDate'] = ccparams.teamsLockInDeadline
    #Ensure teams havent been locked
    if ccparams.teamsLockInDeadline > current_localtime() and ccparams.selfAssignment:
        context_dict['joinable'] = True
    
    context_dict['selfAssignment'] = ccparams.selfAssignment
    
   

    return render(request,'Students/teamList.html', context_dict)
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
    print(studentIDs)

    #get students that aren't in a team
    unassigned_students = []
    for ID in studentIDs:
        ts = TeamStudents.objects.filter(teamID__courseID=course, studentID=ID, activeMember=True)
        #if student has no team
        if not ts and not ID.isTestStudent:
            unassigned_students.append(ID)
    if unassigned_students:
        unassigned_team.teamLeader = unassigned_students[0]
        unassigned_team.save()
    return unassigned_students

def studentTeamJoin(request):
    context_dict,currentCourse = studentInitialContextDict(request)

    if 'teamID' in request.GET:
        team = Teams.objects.get(teamID=request.GET['teamID'], courseID=currentCourse)
        team_student = TeamStudents.objects.get(studentID=context_dict['student'], activeMember=True, teamID__courseID=currentCourse)
        team_student.teamID = team
        team_student.modeOfEnrollment = 'Student'
        team_student.save()
        print(team_student, "XXX")
        
    return redirect('teamList')

    


    

