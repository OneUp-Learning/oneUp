from django.shortcuts import render, redirect
from django.db.models import Q

from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.utils import initialContextDict
from Instructors.constants import anonymous_avatar

from django.contrib.auth.models import User
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from Badges.models import CourseConfigParams
from oneUp.decorators import instructorsCheck 

import logging
logger = logging.getLogger(__name__)

students_per_page = 20
usernameprefix = 'adduser-'

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def addStudentListView(request):

    context_dict, currentCourse = initialContextDict(request)
    context_dict['usernameprefix'] = usernameprefix
    
    # Students not in this class
    srcInCourse = StudentRegisteredCourses.objects.filter(courseID=currentCourse).distinct().values('studentID')
    students = Student.objects.exclude(pk__in=srcInCourse).filter(isTestStudent=False)
    
    if 'partial_name' in request.GET:
        partial_name = request.GET['partial_name']
    
        # Note if union is used instead of |, order_by fails due to bug in Django.
        students = students.filter(Q(user__last_name__icontains=partial_name) | Q(user__first_name__icontains=partial_name) | Q(user__email__icontains=partial_name) | Q(user__username__icontains=partial_name))
        
    if 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 0
    
    context_dict['page'] = page
    num_pages = students.count() / students_per_page
    context_dict['hide_next_page'] = page >= num_pages-1
    context_dict['hide_prev_page'] = page == 0
    context_dict['students'] = students.order_by('user__last_name')[page*students_per_page:(page+1)*students_per_page]
     
    return render(request,'Instructors/AddStudentListView.html', context_dict)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def addExistingStudent(request):
    
    context_dict, currentCourse = initialContextDict(request)
    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
    
    students = []
    
    for value in request.POST:
        if value.startswith(usernameprefix):
            username = value[len(usernameprefix):] # String without the username prefix
            user = User.objects.get(username=username)
            students.append(Student.objects.get(user=user))
        
    for student in students:
        # register the student for this course
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
    
    return redirect('createStudentListView')
