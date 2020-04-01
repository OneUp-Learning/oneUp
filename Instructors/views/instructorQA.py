#  GGM
#  6/23/2018

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from Instructors.views.utils import initialContextDict

@login_required
def instructorQA(request):
    context_dict, currentCourse = initialContextDict(request)          
    return render(request,'Instructors/InstructorQA.html',context_dict)
