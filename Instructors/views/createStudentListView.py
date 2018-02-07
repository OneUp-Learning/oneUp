'''
Created on August 25, 2015

@author: Alex 
'''
from django.template import RequestContext
from django.shortcuts import render

from oneUp.auth import createStudents, checkPermBeforeView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Instructors.models import Courses
from Students.models import Student, StudentRegisteredCourses, StudentEventLog
from Badges.enums import Event
from Badges.systemVariables import logger

@login_required
def createStudentListView(request):

    context_dict = { }
    
    userID = []
    first_Name = []      
    last_Name = []
    user_Email = []  
    user_Action = []   
    user_Avatar = []   

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'  

    courseStudents = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    studentEvents = [Event.startChallenge, Event.endChallenge, Event.userLogin, Event.studentUpload, Event.spendingVirtualCurrency,
                     Event.visitedDashboard, Event.visitedEarnedVCpage, Event.visitedBadgesInfoPage, Event.visitedSpendedVCpage,
                     Event.visitedVCRulesInfoPage]
    for cs in courseStudents:
        s = cs.studentID
        last_action = StudentEventLog.objects.filter(course=currentCourse, student = s, event__in = studentEvents).order_by('-timestamp').first()
        
        userID.append(s.user)
        first_Name.append(s.user.first_name)
        last_Name.append(s.user.last_name)
        user_Email.append(s.user.email)
        if last_action:
            user_Action.append(last_action.timestamp.strftime("%m/%d/%Y %I:%M %p"))
            print()
        else:
            user_Action.append("None")
        user_Avatar.append(cs.avatarImage)
               
    # The range part is the index numbers.
    context_dict['user_range'] = zip(range(1,courseStudents.count()+1),userID,first_Name,last_Name,user_Email,user_Action, user_Avatar)
               
    return render(request,'Instructors/CreateStudentList.html', context_dict)

