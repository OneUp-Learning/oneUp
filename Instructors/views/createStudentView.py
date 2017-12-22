'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.shortcuts import render

from oneUp.auth import createStudents, checkPermBeforeView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Instructors.views.createStudentListView import createStudentListView
from Instructors.views.utils import initialContextDict
from Instructors.models import Courses
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
import logging

logger = logging.getLogger(__name__)

def createStudentView(request):
    checkPermBeforeView(createStudents,request,createStudentViewUnchecked)

@login_required
def createStudentViewUnchecked(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict['usertype'] = 'Student'
    context_dict['message'] = ''
    ccparams = context_dict['ccparams']
        
    if request.POST:
        
        uname = request.POST['uname']
        pword = request.POST['pword']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        uniqueUsername = True   
        
        
        
        #print(a)
        if 'userID' in request.POST:        # edit
            u = User.objects.get(username=request.POST['userID'])
            
            u.first_name = firstname
            u.last_name = lastname
            u.email = email
                #u.username = uname        # uname cannot be changed; if needed, the student must be deleted and a new student created
            if not pword.startswith( 'bcrypt' ):
                u.set_password(pword)
            u.save()
            
        else:
            # new user
            users = User.objects.filter(email = email)
            usersId = User.objects.filter(username = uname)
            print(usersId)
        
            if not users and not usersId:
                user = User.objects.create_user(uname,email,pword)
                user.first_name = firstname
                user.last_name = lastname
                user.save()
                
                student = Student()
                student.user = user
                student.universityID = email
                student.save()
                print("New Student Created")
                
            # oumar
            else:
                if users and usersId:
                    context_dict['user_taken'] = '*Both Email and User ID already in use. Please verify your information.'
                elif usersId:
                    context_dict['user_taken'] = '*User ID already taken. Please choose another User ID.'
                elif users:
                    context_dict['user_taken'] = '*Email already in use. Please verify your information.'
                uniqueUsername = False
                print("this user name is taken")
                return render(request,"Administrators/CreateUser.html", context_dict)
                    
                    # TO DO: need to warn the user that this user name is taken!!!!!! 
            
            if uniqueUsername:
                student = Student.objects.get(user = users)    
                studentRegisteredCourses = StudentRegisteredCourses()
                studentRegisteredCourses.studentID = student
                studentRegisteredCourses.courseID = currentCourse
                studentRegisteredCourses.avatarImage = anonymous_avatar
                if ccparams.virtualCurrencyAdded:
                    studentRegisteredCourses.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
                studentRegisteredCourses.save()
                logger.debug('[POST] Created New Student With VC Amount: ' + str(studentRegisteredCourses.virtualCurrencyAmount))
                # Create new Config Parameters
                scparams = StudentConfigParams()
                scparams.courseID = currentCourse
                scparams.studentID = student
                scparams.save()
        
        return createStudentListView(request)
    else:
        if 'userID' in request.GET:         # render information for editing
            context_dict['userID'] = request.GET['userID']
            studentID = User.objects.filter(username=request.GET['userID'])
            user = Student.objects.filter(user=studentID)
            uname = []
            pword = []
            firstname = []
            lastname = []
            email = []
            for u in user:
                uname.append(u.user.username)
                pword.append(u.user.password)
                firstname.append(u.user.first_name)
                lastname.append(u.user.last_name)
                email.append(u.user.email)
            
            context_dict['user_range'] = zip(firstname,lastname,email,uname,pword) 
        return render(request,"Administrators/CreateUser.html", context_dict)



