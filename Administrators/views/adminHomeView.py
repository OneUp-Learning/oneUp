'''
Created on Sep 10, 2016
Last Updated Sep 20, 2016

'''
from django.template import RequestContext
from django.shortcuts import render

from django.contrib.auth.models import User
from Instructors.models import Courses

def adminHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # Create Administrators List (AH)
    administrators = User.objects.filter(groups__name='Admins')
    print("Admins:", administrators)
    context_dict['administrators'] = administrators
    
    # Create Instructors List (AH)
    instructors = User.objects.filter(groups__name='Teachers').exclude(groups__name='Admins')
    print("Instructors:", instructors)
    context_dict['instructors'] = instructors
    
    # Create Courses List (AH)
    courses = Courses.objects.all()
    print("Courses:", courses)
    course_ID = []
    course_Name = []
    for c in courses:
        course_ID.append(c.courseID)
        course_Name.append(c.courseName)
    context_dict['courses'] = zip(range(1, len(courses)+1), course_ID, course_Name)
    
    return render(request,'Administrators/adminHome.html', context_dict)