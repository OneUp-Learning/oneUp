'''
Created on November 12, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict, is_number
from oneUp.decorators import instructorsCheck
from Instructors.models import (Trivia, 
                                TriviaQuestion)


def generate_trivia_data(context_dict, currentCourse):
    trivia_sessions = Trivia.objects.filter(courseID=currentCourse)
    
    # There should be some kind of null check here for an empty 
    # list probably, but nowhere else in the code could I find 
    # another developer doing such a check.
    
    context_dict['trivia_sessions'] = zip(trivia_sessions)

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def triviaSessionCreateView(request):

    context_dict, currentCourse = initialContextDict(request)

    if request.POST: # submitting a new trivia session
        session_name = request.POST['SessionName']
        max_possible_vc = int(request.POST['maxPossibleVC'])
        max_points_per_question = int(request.POST["maxPossiblePoints"])
        current_trivia = False
        
        if 'triviaID' in request.POST:
            current_trivia = Trivia.objects.filter(triviaID=request.POST['triviaID'], courseID=currentCourse)
            
        if current_trivia and (current_trivia.exists()):
            current_trivia = current_trivia[0] # get the first (only?) trivia object available.
            current_trivia.triviaName = session_name
            current_trivia.maximumPointsPerQuestion = max_points_per_question
            current_trivia.maximumVCPossible = max_possible_vc
            current_trivia.save()
            
        else: # Create a new trivia session
            new_trivia_object = Trivia()
            new_trivia_object.courseID = currentCourse
            new_trivia_object.triviaName = session_name
            new_trivia_object.maximumPointsPerQuestion = max_points_per_question
            new_trivia_object.maximumVCPossible = max_possible_vc
            new_trivia_object.save()
            
        return redirect('/oneUp/instructors/TriviaDashboard', context_dict)
    
    else: # Requesting data about a session or modifying
        if ('triviaID' in request.GET) and (is_number(request.GET['triviaID'])):
            trivia = Trivia.objects.filter(courseID=currentCourse, triviaID=request.GET['triviaID'])
            
            if trivia.exists():
                trivia = trivia[0]
                context_dict['triviaID'] = trivia.triviaID
                context_dict['triviaName'] = trivia.triviaName
                context_dict['maxPoints'] = trivia.maximumPointsPerQuestion
                context_dict['maxVC'] = trivia.maximumVCPossible
                context_dict['questionCount'] = TriviaQuestion.objects.filter(triviaID=trivia).count()
            
        generate_trivia_data(context_dict, currentCourse)

        return render(request, 'Instructors/TriviaSessionSetup.html', context_dict)
