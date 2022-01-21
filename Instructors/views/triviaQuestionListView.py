'''
Created on December 13, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck

def initialize_question_data(context_dict, currentCourse):
    # Do trivia question data generation here
    print('Generate data')

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def createTriviaQuestionListView(request):

    context_dict, currentCourse = initialContextDict(request)

    initialize_question_data(context_dict, currentCourse)

    return render(request, 'Instructors/TriviaQuestionList.html', context_dict)
