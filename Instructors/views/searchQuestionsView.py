'''
Created on Apr 10, 2014

@author: dichevad
'''
from django.shortcuts import render

from django.template import RequestContext
from django.shortcuts import render

from django.http import HttpResponse

from Instructors.models import Questions, Tags, Courses, Challenges
#from Instructors.models import QuestionTypes
from Badges.enums import QuestionTypes, dict_dict_to_zipped_list

from django.contrib.auth.decorators import login_required

@login_required
def searchQuestions(request):
 
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

    typename = []      
    tags = []    
    leveldiffs = []
    qchallenge = []
    qdifficulty = []
    qdifficulties = ['Easy', 'Medium', 'Hard']


    # Get information for question types to display on the search page       
    questionTypesObjects= dict_dict_to_zipped_list(QuestionTypes.questionTypes,['index','displayName'])
     
    # information about the level of difficulty
    num_qdifficulties = len(qdifficulties)
    for i in range(0, num_qdifficulties):
        qdifficulty.append(qdifficulties[i])
        
            
    # Get challenges from the DB
    challenges = Challenges.objects.filter(courseID=currentCourse)
    num_challenges = challenges.count()
    for i in range(0, num_challenges):
        qchallenge.append(challenges[i].challengeName)
        
    context_dict['qtypes_range'] = questionTypesObjects
    #context_dict['qtypes_range'] = zip(range(1, num_qtypes + 1), typename)
    context_dict['qdifficulty_range'] = zip(range(1, num_qdifficulties + 1), qdifficulty)
    context_dict['challenge_range'] = zip(range(1, num_challenges + 1), qchallenge)
    
    if 'challengeID' in request.GET:         
        context_dict['challenge'] = True
        context_dict['challengeID'] = request.GET['challengeID']
        challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
        context_dict['challengeName'] = challenge.challengeName

    return render(request,'Instructors/SearchQuestions.html', context_dict)
        
        
