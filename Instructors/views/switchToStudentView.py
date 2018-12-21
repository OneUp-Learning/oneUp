'''
Created on Sep 2, 2018

@author: oumar
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck   
  

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def switchToStudentView(request):
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"]=user.username
        
        if 'teacher' in request.GET:
            if 'courseID' in request.GET:
                return redirect('/oneUp/students/StudentCourseHome')
            else:
                return redirect('/oneUp/students/StudentHome')
            
    return render(request, 'oneUp/home.html', context_dict)
        
        