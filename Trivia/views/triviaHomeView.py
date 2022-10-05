from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from Instructors.views.utils import initialContextDict
from Students.views.utils import studentInitialContextDict
from Students.models import Student


def triviaHomeView(request):
    user = request.user
    
    # anonymous user test
    if user.is_anonymous:
        return redirect('/oneUp/home')
    
    if 'triviaID' in request.GET:
        request.session['triviaID'] = request.GET['triviaID']
    if not Student.objects.get(user=user).isTestStudent:
        isStudent = True
        print("Student")
        context_dict,currentCourse = studentInitialContextDict(request)
        if not context_dict['ccparams'].triviaEnabled or not 'triviaID' in request.session:
            return redirect(request.META.get('HTTP_REFERER', '/oneUp/students/StudentCourseHome'))
        else:
            return redirect(request.META.get('HTTP_REFERER', '/oneUp/trivia/triviaHome/player'))
    else:
        isStudent = False
        print("Teacher")
        context_dict, currentCourse = initialContextDict(request)
        if not context_dict['ccparams'].triviaEnabled or not 'triviaID' in request.session:
            return redirect(request.META.get('HTTP_REFERER', '/oneUp/instructors/instructorCourseHome'))
        else:
            return redirect(request.META.get('HTTP_REFERER', '/oneUp/trivia/triviaHome/game'))
        
