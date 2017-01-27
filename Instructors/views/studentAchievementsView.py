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
from Students.models import Student, StudentRegisteredCourses
    
@login_required
def studentAchievements(request):
 
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        userID = []
        first_Name = []      
        last_Name = []
        user_Email = []         
        
        # Only shows students that are registred in the current course (AH)
        user = StudentRegisteredCourses.objects.filter(courseID=request.session['currentCourseID'])
        for u in user:
            student = u.studentID
            userID.append(student)
            #print(u.studentID.user)
            first_Name.append(student.user.first_name)
            last_Name.append(student.user.last_name)
            user_Email.append(student.user.email)
            
        # The range part is the index numbers.
        context_dict['user_range'] = zip(range(1,user.count()+1),first_Name,last_Name,user_Email,userID) 

    return render(request,'Instructors/StudentAchievements.html', context_dict)
