'''
Created on December 12, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Students.views.utils import studentInitialContextDict

def initialize_trivia_context_dict(context_dict, currentCourse):
	# Do trivia data generation here
	print('Generate data')

@login_required
def createTriviaDashboard(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    initialize_trivia_context_dict(context_dict, currentCourse)

    return render(request, 'Students/TriviaDashboard.html', context_dict)