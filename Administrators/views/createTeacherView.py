'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.template import RequestContext
from django.shortcuts import render, redirect

from oneUp.auth import createTeachers, checkPermBeforeView, teachers
from django.contrib.auth.models import User
from Badges.systemVariables import logger
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams

def createTeacherView(request):
    checkPermBeforeView(createTeachers,request,createTeacherViewUnchecked)

def createTeacherViewUnchecked(request):
    context_dict = {}
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
    
    st = Student.objects.all()
    print(st)
    if request.method == 'POST':
        uname = request.POST['instructorUsername']
        pword = request.POST['instructorPassword']
        firstname = request.POST['instructorFirstName']
        lastname = request.POST['instructorLastName']
        email = request.POST['instructorEmail']
        
        instructors = User.objects.filter(groups__name="Teachers", username=uname)
        instructorEmails = User.objects.filter(groups__name="Teachers", email= email)

        errorList = []
        if 'instructorID' in request.GET:
            if uname == request.POST['iUsernamePrev'] and email == request.POST['iEmailPrev']: # If the username and email has not been changed
                instructor = instructors[0]
                instructor.first_name = firstname
                instructor.last_name = lastname
                if not pword.startswith('bcrypt'):
                    instructor.set_password(pword)
                instructor.save()
                
                student = Student.objects.filter(user=instructor)
                if student:
                    student = student[0]
                    student.first_name = firstname
                    student.last_name = lastname
                    if not pword.startswith('bcrypt'):
                        student.set_password(pword)
                    student.save()
                    
            if instructors and instructors[0].username != request.POST['iUsernamePrev']: 
                errorList.append("Instructor username is taken.")
            if instructorEmails and instructorEmails[0].email != request.POST['iEmailPrev']:
                errorList.append("Instructor email is taken.")
            if len(errorList) == 0: # The username and email are unique
                instructor = instructors[0]
                instructor.username = uname
                instructor.first_name = firstname
                instructor.last_name = lastname
                instructor.email = email
                if not pword.startswith('bcrypt'):
                    instructor.set_password(pword)
                instructor.save()
                
                student = Student.objects.filter(user=instructor)
                if student:
                    student = student[0]
                    student.first_name = firstname
                    student.last_name = lastname
                    if not pword.startswith('bcrypt'):
                        student.set_password(pword)
                    student.save()
        else: # Creating a new instructor
            if instructors:
                errorList.append("Instructor username is taken.")
            if instructorEmails:
                errorList.append("Instructor email is taken.")
            if len(errorList) == 0:
                user = User.objects.create_user(uname,email,pword)
                
                user.first_name = firstname
                user.last_name = lastname
                user.groups.add(teachers)
                user.save()
                
                # Create a test student while creating a new instructor
                student = Student()
                student.user = user
                student.universityID = email
                student.isTestStudent = True
                student.save()  
                
        context_dict['errorMessages'] = errorList
        
    context_dict['view'] = False
    instructors = User.objects.filter(groups__name='Teachers')
    context_dict['instructors'] = instructors
    if 'instructorID' in request.GET:
        instructor = User.objects.get(groups__name="Teachers", username=request.GET['instructorID'])
        context_dict['instructorUsername'] = instructor.username
        context_dict['instructorPassword'] = instructor.password
        context_dict['instructorFirstName'] = instructor.first_name
        context_dict['instructorLastName'] = instructor.last_name
        context_dict['instructorEmail'] = instructor.email
        
        context_dict['editInstructor'] = True

    return render(request,"Administrators/createTeacher.html", context_dict)

