'''
Created on December 12, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck

def initialize_trivia_context_dict(context_dict, currentCourse):
	# Do trivia data generation here
	print('Generate data')

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def createTriviaDashboard(request):

    context_dict, currentCourse = initialContextDict(request)

    initialize_trivia_context_dict(context_dict, currentCourse)

    return render(request, 'Students/TriviaDashboard.html', context_dict)
