from django.shortcuts import render, redirect

from oneUp.auth import createStudents, checkPermBeforeView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.createStudentListView import createStudentListView
from Students.views.utils import studentInitialContextDict
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from oneUp.decorators import instructorsCheck  
import logging

logger = logging.getLogger(__name__)

@login_required
def resetPasswordView(request):
 
    context_dict, currentCourse = studentInitialContextDict(request)
        
    if request.method == 'POST':
        
        username = request.POST['username']
        old_password = request.POST['old_password']
        new_password = request.POST['new_password'].strip()
        student = context_dict['student'].user

        if context_dict['is_test_student'] == True:
            return redirect('/oneUp/students/StudentCourseHome')
            
        student.set_password(new_password)
        student.save()

        return redirect('/oneUp/home')
    return render(request,"Students/ResetPassword.html", context_dict)
    
@login_required
def validateResetPassword(request):
    from django.http import JsonResponse

    context_dict, currentCourse = studentInitialContextDict(request)
    username = request.POST['username'].strip()
    old_password = request.POST['old_password'].strip()
    new_password = request.POST['new_password'].strip()
    new_password_confirm = request.POST['new_password_confirm'].strip()

    student = context_dict['student']
    
    errorList = []
    if old_password == new_password:
        errorList.append("New password is the same as the old password")
    valid = student.user.check_password(old_password)
    if not valid:
        errorList.append("Old password is incorrect")
    if username != student.user.username:
        errorList.append("Username is incorrect")
    if new_password == "":
        errorList.append("Please enter a new password")
    if new_password_confirm != new_password:
        errorList.append("New password and confirm password do not match")

    response = {}
    response['errorMessages'] = errorList
    return JsonResponse(response)

