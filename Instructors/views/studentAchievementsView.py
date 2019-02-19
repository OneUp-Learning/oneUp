'''
Created on August 25, 2015

@author: Alex 
'''
from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.utils import initialContextDict
from Students.models import StudentRegisteredCourses
from oneUp.decorators import instructorsCheck     
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def studentAchievements(request):
 
    context_dict, currentCourse = initialContextDict(request)

    userID = []
    first_Name = []      
    last_Name = []
    user_Email = []         
    
    # Only shows students that are registred in the current course (AH)
    user = StudentRegisteredCourses.objects.filter(courseID=request.session['currentCourseID']).exclude(studentID__isTestStudent=True)
    for u in user:
        student = u.studentID
        userID.append(student)
        #print(u.studentID.user)
        first_Name.append(student.user.first_name)
        last_Name.append(student.user.last_name)
        user_Email.append(student.user.email)
        
    # The range part is the index numbers.
    context_dict['user_range'] = sorted(list(zip(range(1,user.count()+1),first_Name,last_Name,user_Email,userID) ), key=lambda tup: tup[2])
    context_dict['is_teacher'] = True
        

    return render(request,'Instructors/StudentAchievements.html', context_dict)
