'''
Created on August 25, 2015

@author: Alex 
'''
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict
from Students.models import StudentRegisteredCourses, StudentEventLog
from Badges.enums import Event

@login_required
def createStudentListView(request):

    context_dict, currentCourse = initialContextDict(request)
    
    userID = []
    first_Name = []      
    last_Name = []
    user_Email = []  
    user_Action = []   
    user_Avatar = []   

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
            user_Action.append(last_action.timestamp)
        else:
            user_Action.append("None")
        user_Avatar.append(cs.avatarImage)
               
    # The range part is the index numbers.
    context_dict['user_range'] = sorted(list(zip(range(1,courseStudents.count()+1),userID,first_Name,last_Name,user_Email,user_Action, user_Avatar)), key=lambda tup: tup[3])
               
    return render(request,'Instructors/CreateStudentList.html', context_dict)

