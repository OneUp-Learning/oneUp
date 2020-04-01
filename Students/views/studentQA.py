#  GGM
#  6/23/2018

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from Students.views.utils import studentInitialContextDict

@login_required
def studentQA(request):
    context_dict, currentCourse = studentInitialContextDict(request) 
    
    return render(request,'Students/StudentQA.html',context_dict)