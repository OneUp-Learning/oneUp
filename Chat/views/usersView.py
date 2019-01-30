from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.serializers import UserSerializer, CourseSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import json, re
from django.shortcuts import redirect

from Instructors.views.utils import initialContextDict
from Students.views.utils import checkIfAvatarExist
from Students.models import Student, StudentRegisteredCourses

class UserView(APIView):
    renderer_classes = (JSONRenderer, )
    
    def get(self, request, format=None):
        ''' Returns active signin user and course'''

        user = request.user
        context_dict, current_course = initialContextDict(request)

        student = Student.objects.get(user=user)
        is_test_student = student.isTestStudent
        is_teacher = False
        if is_test_student:
            is_teacher = True
        
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=current_course)
        avatar = checkIfAvatarExist(st_crs)

        user_serializer = UserSerializer(user)
        course_serializer = CourseSerializer(current_course)

        course_students = StudentRegisteredCourses.objects.filter(courseID=current_course)
        student_avatars = {}
        for student in course_students:
            user_id = student.studentID.user.id
            student_avatar = checkIfAvatarExist(student)
            student_isteacher = student.studentID.isTestStudent
            student_avatars[user_id] = {'avatar': student_avatar, 'is_teacher': student_isteacher}

        return Response({'user': user_serializer.data, 'course': course_serializer.data, 'is_teacher': is_teacher, 'avatar': avatar, 'student_avatars': student_avatars})

