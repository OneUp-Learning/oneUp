'''
Created on Sep 6, 2018

@author: omar
'''

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from Instructors.models import InstructorRegisteredCourses
from Instructors.constants import anonymous_avatar
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def resetTestStudent(request):
    context_dict = {}

    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"] = user.username

        if Student.objects.filter(user=user):
            # Delete teststudent and recreate it and register it to the course(s)
            Student.objects.get(user=user).delete()

        # Recreate testStudent and register it to the course(s)
        student = Student()
        student.user = user
        student.universityID = user.email
        student.isTestStudent = True
        student.save()

        ircs = InstructorRegisteredCourses.objects.filter(instructorID=user)

        for course in ircs:
            student = Student.objects.get(user=user)
            studentRegisteredCourses = StudentRegisteredCourses()
            studentRegisteredCourses.studentID = student
            studentRegisteredCourses.courseID = course.courseID
            studentRegisteredCourses.avatarImage = anonymous_avatar
            studentRegisteredCourses.save()

            # Configure params for test student
            scparams = StudentConfigParams()
            scparams.courseID = course.courseID
            scparams.studentID = student
            scparams.save()

        if 'courseID' in request.POST:
            context_dict['courseID'] = request.POST['courseID']
            return redirect('/oneUp/instructors/instructorCourseHome')
        else:
            return redirect('/oneUp/instructors/instructorHome')

    else:
        return render(request, 'oneUp/home.html', context_dict)
