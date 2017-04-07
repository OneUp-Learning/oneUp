'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.template import RequestContext
from django.shortcuts import render

from oneUp.auth import createStudents, checkPermBeforeView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Instructors.views.createStudentListView import createStudentListView
from Instructors.models import Courses
from Instructors import constants
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses

@login_required
def createStudentView(request):
    checkPermBeforeView(createStudents,request,createStudentViewUnchecked)

def createStudentViewUnchecked(request):
 
    context_dict = { 'usertype':'Student', 'message':'' }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
        currentCourse = 1
        
    if request.POST:
        
        uname = request.POST['uname']
        pword = request.POST['pword']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']   
        if 'userID' in request.POST:
            u = User.objects.get(username=request.POST['userID'])
            u.first_name = firstname
            u.last_name = lastname
            u.email = email
            u.username = uname
            if not pword.startswith( 'bcrypt' ):
                u.set_password(pword)
            u.save()
            
        else:    
            user = User.objects.create_user(uname,email,pword)
            user.first_name = firstname
            user.last_name = lastname
            user.save()
            
            student = Student()
            student.user = user
            student.universityID = email
            student.avatarImage = constants.anonymous_avatar
            student.save()
            
            context_dict['message'] = '<B>New Student '+uname+' created!</B>'
    
            studentRegisteredCourses = StudentRegisteredCourses()
            studentRegisteredCourses.studentID = student
            studentRegisteredCourses.courseID = currentCourse
            studentRegisteredCourses.avatarImage = anonymous_avatar
            studentRegisteredCourses.save()
        
        return createStudentListView(request)
    else:
        if 'userID' in request.GET:
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



