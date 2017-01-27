'''
Created on Apr 7, 2014

@author: dichevad
'''
from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import Courses, Challenges
from Instructors.views import challengeListView

from django.contrib.auth.decorators import login_required

@login_required
def challengeQuestionSelectView(request):
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
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse)
    else:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'

    chal_ID = []      #PK for existing answers
    chal_preview = []         
    chal_type = []

#     if request.GET:
        
    challenges = Challenges.objects.all()
    for chal in challenges:
        chal_ID.append(chal.questionID)
        chal_preview.append(chal.preview)
        chal_type.append(chal.type)
            
        # The range part is the index numbers.
    context_dict['chal_range'] = zip(range(1,challenges.count()+1),chal_ID,chal_preview,chal_type)

    return render(request,'Instructors/ChallengeQuestionSelect.html', context_dict)
