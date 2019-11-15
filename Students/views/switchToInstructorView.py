'''
Created on Sep 2, 2018

@author: omar
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def switchToInstructorView(request):
    context_dict = {}

    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"] = user.username

        if 'student' in request.GET:
            if 'courseId' in request.GET:
                return redirect('/oneUp/instructors/instructorCourseHome')
            else:
                return redirect('/oneUp/instructors/instructorHome')

    return render(request, '/oneUp/home.html', context_dict)
