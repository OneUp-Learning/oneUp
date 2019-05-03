from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.models import Channel, Message
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import json, re
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from Instructors.views.utils import initialContextDict
from Students.views.utils import studentInitialContextDict
from Students.models import Student

@ensure_csrf_cookie
def chat(request):
    user = request.user
    # Teachers are students too ;)
    if not Student.objects.get(user=user).isTestStudent:
        print("Student")
        context_dict,currentCourse = studentInitialContextDict(request)
        if not context_dict['ccparams'].chatUsed:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/oneUp/students/StudentCourseHome'))
    else:
        print("Teacher")
        context_dict, currentCourse = initialContextDict(request)
        if not context_dict['ccparams'].chatUsed:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/oneUp/instructors/instructorCourseHome'))

    channel, _ = Channel.objects.get_or_create(channel_name="generic", course=currentCourse)
    
    if not Channel.objects.filter(channel_name="generic", users=user, course=currentCourse).exists():
        channel.users.add(user)
        channel.save()

    return render(request, 'Chat/chat.html', context_dict)
