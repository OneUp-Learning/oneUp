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
    # Test for anonymous user
    if user.is_anonymous:
        return redirect('/oneUp/home')
    # Teachers are students too ;)
    if not Student.objects.get(user=user).isTestStudent:
        print("Student")
        context_dict,currentCourse = studentInitialContextDict(request)
        if not context_dict['ccparams'].triviaEnabled:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/oneUp/students/StudentCourseHome'))
    else:
        print("Teacher")
        context_dict, currentCourse = initialContextDict(request)
        if not context_dict['ccparams'].triviaEnabled:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/oneUp/instructors/instructorCourseHome'))

    return render(request, 'Trivia/trivia.html', context_dict)
