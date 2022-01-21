'''
Created on November 15, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Instructors.models import (Trivia, 
                                TriviaQuestion)

def generate_trivia_data(context_dict, currentCourse):
    trivia_sessions = Trivia.objects.filter(courseID=currentCourse)
    
    # There should be some kind of null check here for an empty 
    # list probably, but nowhere else in the code could I find 
    # another developer doing such a check.
    valid_sessions = []
    
    for session in trivia_sessions:
        session_data = {'triviaID': session.triviaID, 'triviaName': session.triviaName}
        valid_sessions.append(session_data)
        
    context_dict['trivia_sessions'] = list(zip(range(len(valid_sessions)), valid_sessions))

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def createTriviaDashboard(request):

    context_dict, currentCourse = initialContextDict(request)

    generate_trivia_data(context_dict, currentCourse)

    return render(request, 'Instructors/TriviaDashboard.html', context_dict)
