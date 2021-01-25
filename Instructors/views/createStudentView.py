'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.shortcuts import render

from oneUp.auth import createStudents, checkPermBeforeView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.createStudentListView import createStudentListView
from Instructors.views.utils import initialContextDict
from Instructors.views.preferencesView import createSCVforInstructorGrant
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from oneUp.decorators import instructorsCheck       
import smtplib

import logging

logger = logging.getLogger(__name__)

def sendEmail(recipient, subject, body):
    gmail_user = 'oneupemailer@gmail.com'
    gmail_password = 'vtrenmzgsahmfgcv'
    
    to = [recipient]
    
    email_text = 'Subject: {}\n\n{}'.format(subject, body)
    
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
        server.set_debuglevel(1)
        server.login(gmail_user, gmail_password)
        text = email_text
        server.sendmail(gmail_user, to[0], text)
        server.quit()
        
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def createStudentView(request):
    checkPermBeforeView(createStudents,request,createStudentViewUnchecked)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def createStudentViewUnchecked(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict['usertype'] = 'Student'
    ccparams = context_dict['ccparams']
        
    if request.method == 'POST':
        
        uname = request.POST['uname']
        pword = request.POST['pword']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        students = User.objects.filter(username=uname)
        
        if 'userID' in request.POST: # Update student information
            # username cannot be changed; if needed, the student must be deleted and a new student created
            if students:
                student = students[0]
            else:
                students = User.objects.filter(username=request.POST['userID'])
                student = students[0]
                student.username = uname

            student.first_name = firstname
            student.last_name = lastname
            student.email = email
            
            if not pword.startswith('bcrypt'):
                student.set_password(pword)
            student.save()


        else:
            students = User.objects.filter(username=uname)
            if students:
                # Student is created but is not added to this course so add the student
                student = Student.objects.get(user = students[0])
                
                studentRegisteredCourses = StudentRegisteredCourses()
                studentRegisteredCourses.studentID = student
                studentRegisteredCourses.courseID = currentCourse
                studentRegisteredCourses.avatarImage = anonymous_avatar
                if ccparams.virtualCurrencyAdded:
                    # We have now switched to the canonical virtual currency amount a student has being determined by their transactions,
                    # so we first add a StudentVirtualCurrency entry to show their gain and then we adjust the virtualCurrencyAmount.
                    createSCVforInstructorGrant(student,currentCourse,ccparams.virtualCurrencyAdded)
                    studentRegisteredCourses.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
                studentRegisteredCourses.save()
                
                logger.debug('[POST] Created New Student With VC Amount: ' + str(studentRegisteredCourses.virtualCurrencyAmount))
                
                # Create new Config Parameters
                scparams = StudentConfigParams()
                scparams.courseID = currentCourse
                scparams.studentID = student
                scparams.save()
            else:
                # New student entirely
                user = User.objects.create_user(uname,email,pword)
                user.first_name = firstname
                user.last_name = lastname
                user.save()
                
                student = Student()
                student.user = user
                student.universityID = email
                student.save()

                sendEmail(email, "Welcome to OneUp!", 
"""Hello """+firstname+""",

    Your account has been created, please use the following credentials to sign-in.
    
    User Name: """+email+"""
    Password: """+pword+"""
    
OneUp Admin"""
            )
                
                print("New Student Created")        
                        
                studentRegisteredCourses = StudentRegisteredCourses()
                studentRegisteredCourses.studentID = student
                studentRegisteredCourses.courseID = currentCourse
                studentRegisteredCourses.avatarImage = anonymous_avatar
                if ccparams.virtualCurrencyAdded:
                    # We have now switched to the canonical virtual currency amount a student has being determined by their transactions,
                    # so we first add a StudentVirtualCurrency entry to show their gain and then we adjust the virtualCurrencyAmount.
                    createSCVforInstructorGrant(student,currentCourse,ccparams.virtualCurrencyAdded)
                    studentRegisteredCourses.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
                studentRegisteredCourses.save()
                
                logger.debug('[POST] Created New Student With VC Amount: ' + str(studentRegisteredCourses.virtualCurrencyAmount))
    
                # Create new Config Parameters
                scparams = StudentConfigParams()
                scparams.courseID = currentCourse
                scparams.studentID = student
                scparams.save()

        return createStudentListView(request)
    elif request.method == 'GET':
        if 'userID' in request.GET:         # render information for editing
            context_dict['userID'] = request.GET['userID']
            studentID = User.objects.get(username=request.GET['userID'])
            
            context_dict['uname'] = studentID.username
            context_dict['pword'] = studentID.password
            context_dict['firstname'] = studentID.first_name
            context_dict['lastname'] = studentID.last_name
            context_dict['email'] = studentID.email
            context_dict['pk'] = Student.objects.get(user=studentID).pk
            
        return render(request,"Administrators/createUser.html", context_dict)
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def validateCreateStudent(request):
    from django.http import JsonResponse

    context_dict, currentCourse = initialContextDict(request)
    uname = request.POST['uname']
    pword = request.POST['pword']
    pword2 = request.POST['pword2']
    email = request.POST['email']
    
    students = User.objects.filter(username=uname)
    studentEmails = User.objects.filter(email= email)
    errorList = []
    if 'userID' in request.POST:           
        if students and students[0].username != request.POST['sUsernamePrev']: 
            errorList.append("Student username is taken.")
        if studentEmails and studentEmails[0].email != request.POST['sEmailPrev']:
            errorList.append("Student email is taken.")
    else: # Creating a new student
        if pword != pword2:
            errorList.append("Student passwords do not match.")
        if students:
            errorList.append("Student username is taken.")
        if studentEmails:
            errorList.append("Student email is taken.")
        if students:
            studentID = Student.objects.get(user = students[0])
            if StudentRegisteredCourses.objects.filter(studentID=studentID,courseID =currentCourse).exists():
                errorList.append("Student is already registered in this course.")
        
        
    context_dict['errorMessages'] = errorList
    context_dict['ccparams'] = None
    return JsonResponse(context_dict)

