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
from Students.models import Student
    
def createContextForStudentList():
    context_dict = { }

    userID = []
    first_Name = []      
    last_Name = []
    user_Email = []  
    user_Login = []      
    #universityID = [] 
    
    user = Student.objects.all()
    for u in user:
        userID.append(u.user)
        #universityID.append(u.universityID)
        first_Name.append(u.user.first_name)
        last_Name.append(u.user.last_name)
        user_Email.append(u.user.email)
        user_Login.append(u.user.last_login)
                    
    # The range part is the index numbers.
    context_dict['user_range'] = zip(range(1,user.count()+1),userID,first_Name,last_Name,user_Email,user_Login)
    return context_dict


@login_required
def createStudentListView(request):
 
    context_dict = createContextForStudentList()

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'  
    return render(request,'Instructors/CreateStudentList.html', context_dict)

