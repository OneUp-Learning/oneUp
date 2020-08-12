'''
Created on Sep 2, 2018

@author: oumar
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from Instructors.models import InstructorRegisteredCourses
from Instructors.constants import anonymous_avatar
from Badges.models import CourseConfigParams
from Instructors.views.preferencesView import createSCVforInstructorGrant

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def switchToStudentView(request):
    context_dict = {}

    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"] = user.username

        if not Student.objects.filter(user=user):

            student = Student()
            student.user = user
            student.universityID = user.email
            student.isTestStudent = True
            student.save()

            ircs = InstructorRegisteredCourses.objects.filter(
                instructorID=user)

            for course in ircs:
                student = Student.objects.get(user=user)
                studentRegisteredCourses = StudentRegisteredCourses()
                studentRegisteredCourses.studentID = student
                studentRegisteredCourses.courseID = course.courseID
                studentRegisteredCourses.avatarImage = anonymous_avatar
                ccparams = CourseConfigParams.objects.get(courseID = course)
                if ccparams.virtualCurrencyAdded:
                    # We have now switched to the canonical virtual currency amount a student has being determined by their transactions,
                    # so we first add a StudentVirtualCurrency entry to show their gain and then we adjust the virtualCurrencyAmount.
                    createSCVforInstructorGrant(student,course,ccparams.virtualCurrencyAdded)
                    studentRegisteredCourses.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
                studentRegisteredCourses.save()

                # Configure params for test student
                scparams = StudentConfigParams()
                scparams.courseID = course.courseID
                scparams.studentID = student
                scparams.save()

        if 'teacher' in request.GET:
            if 'courseID' in request.GET:
                return redirect('/oneUp/students/StudentCourseHome')
            else:
                return redirect('/oneUp/students/StudentHome')

    return render(request, 'oneUp/home.html', context_dict)
