'''
Created on Oct 23, 2020

@author: ismith
'''
import json
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Trivia, TriviaAnswer, TriviaQuestion
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def DoSomething(request):
    # AJAX Handler for trivia questions
    context_dict, currentCourse = initialContextDict(request)
    
    #if request.method