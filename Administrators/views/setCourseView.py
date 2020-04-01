'''
Created on Feb 20, 2015

Last updated on Sep 12, 2016
'''
from django.template import RequestContext
from django.shortcuts import redirect
from Instructors.models import Universities, UniversityCourses, Courses
from django.conf import settings

def setCourseView(request):
 
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        
    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']
        university = UniversityCourses.objects.filter(courseID=request.POST['courseID']).first()
        timezone = settings.TIME_ZONE
        if university:
            timezone = university.universityID.universityTimezone

        request.session['django_timezone'] = timezone

    user = request.user    
    
    if user.groups.filter(name='Teachers').exists() and not 'is_student' in request.POST:
        context_dict["is_teacher"] = True
        return redirect('instructorCourseHome')
    elif user.groups.filter(name='Admins').exists() and not 'is_student' in request.GET:
        context_dict["is_admin"] = True
        return redirect('adminHomeView')
    else:
        context_dict["is_student"] = True
        return redirect('StudentCourseHome')

    
 