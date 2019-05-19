'''
Created on August 25, 2015

@author: Alex 
'''
from django.shortcuts import render

from django.contrib.auth.decorators import login_required,  user_passes_test
from Instructors.views.utils import initialContextDict
from Students.models import StudentRegisteredCourses, StudentEventLog
from Badges.enums import Event
from Students.views.avatarView import checkIfAvatarExist
from oneUp.decorators import instructorsCheck    

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def createStudentListView(request):
    print("CSV.canvas", CSV.information[CSV.canvas]['display_name'])
    context_dict, currentCourse = initialContextDict(request)
    
    userID = []
    first_Name = []      
    last_Name = []
    user_Email = []  
    user_Action = []   
    user_Avatar = []  

    

    courseStudents = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)
    studentEvents = [Event.startChallenge, Event.endChallenge, Event.userLogin, Event.studentUpload, Event.spendingVirtualCurrency,
                     Event.visitedDashboard, Event.visitedEarnedVCpage, Event.visitedBadgesInfoPage, Event.visitedSpendedVCpage,
                     Event.visitedVCRulesInfoPage]
    for cs in courseStudents:
        s = cs.studentID
        last_action = StudentEventLog.objects.filter(course=currentCourse, student = s, event__in = studentEvents).order_by('-timestamp').first()
        
        userID.append(s.user)
        print(s)
        first_Name.append(s.user.first_name)
        last_Name.append(s.user.last_name)
        user_Email.append(s.user.email)
        if last_action:
            user_Action.append(last_action.timestamp)
        else:
            user_Action.append("None")
        
        user_Avatar.append(checkIfAvatarExist(cs))
               
    # The range part is the index numbers.
    context_dict['user_range'] = sorted(list(zip(range(1,courseStudents.count()+1),userID,first_Name,last_Name,user_Email,user_Action, user_Avatar)), key=lambda tup: tup[3])
    context_dict['file_types'] = CSV.information.items()
    return render(request,'Instructors/CreateStudentList.html', context_dict)

            
class CSV:
    canvas = 0
    oneUp = 1
    information = {
           canvas:{
                'index': canvas,
                'display_name': 'Canvas'
                },
            oneUp:{
                'index': oneUp,
                'display_name': 'OneUp'
                }
    }