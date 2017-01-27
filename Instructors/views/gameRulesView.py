
from django.shortcuts import render

from django.template import RequestContext
from django.shortcuts import render

from django.http import HttpResponse

from Instructors.models import Courses 
from Instructors.models import Skills

from django.contrib.auth.decorators import login_required

@login_required
def gameRulesView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
             
    return render(request,'Instructors/GameRules.html', context_dict)