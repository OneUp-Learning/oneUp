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
from Instructors.views.utils import initialContextDict, sendEmail
from Instructors.views.preferencesView import createSCVforInstructorGrant
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams, StudentPlayerType
from Instructors.models import UniversityCourses, Universities
from oneUp.decorators import instructorsCheck       
from Badges.models import PlayerType

import logging

logger = logging.getLogger(__name__)

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
        
        #get university email postfix from database
        university_course = UniversityCourses.objects.get(courseID=currentCourse)
        university = university_course.universityID
        postfix = university.universityPostfix
        uname = request.POST['uname']

        #incase instructor included @postfix, remove it
        if '@' in uname:
            idx=request.POST['uname'].index('@')
            uname = uname[:idx]

        uname = uname+'@'+postfix
        pword = request.POST['pword']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        
        playertype = None
        
        if 'playertype' in request.POST:
            if request.POST['playertype'] != 'None':
                playertype = PlayerType.objects.get(name=request.POST['playertype'])
            
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
            
            student_object = Student.objects.get(user=student)
            
            student_playertype = StudentPlayerType.objects.filter(course=currentCourse, student=student_object)
            
            if playertype: # If the playertype was sent as something other than "None"
                if student_playertype.exists():
                    student_playertype[0].playerType=playertype
                    student_playertype[0].save()
                else:
                    new_player_type = StudentPlayerType()
                    new_player_type.student = student_object
                    new_player_type.course = currentCourse
                    new_player_type.playerType = playertype
                    new_player_type.save()
            else: # If the playertype was sent as "None", write "None" to the database entry for the player
                if student_playertype.exists():
                    student_playertype[0].delete()
            
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
                
                if playertype:
                    new_player_type = StudentPlayerType()
                    new_player_type.student = student
                    new_player_type.course = currentCourse
                    new_player_type.playerType = playertype
                    new_player_type.save()
                
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
                if playertype:
                    new_player_type = StudentPlayerType()
                    new_player_type.student = student
                    new_player_type.course = currentCourse
                    new_player_type.playerType = playertype
                    new_player_type.save()
                
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
        context_dict['playertypes'] = PlayerType.objects.filter(course=currentCourse)
            
        if 'userID' in request.GET:         # render information for editing
            context_dict['userID'] = request.GET['userID']
            studentID = User.objects.get(username=request.GET['userID'])
            student_object = Student.objects.get(user=studentID)
            
            context_dict['uname'] = studentID.username
            context_dict['pword'] = studentID.password
            context_dict['firstname'] = studentID.first_name
            context_dict['lastname'] = studentID.last_name
            context_dict['email'] = studentID.email
            context_dict['pk'] = student_object.pk
            
            if ccparams.adaptationUsed:
                player_type = StudentPlayerType.objects.filter(course=currentCourse, student=student_object).first()
                if player_type:
                    context_dict['currentplayertype'] = player_type.playerType
                else:
                    print('no player found')
            
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

