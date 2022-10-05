'''
Created on November 12, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Instructors.models import (Trivia, 
                                TriviaQuestion)


def generate_trivia_review_data(context_dict, currentCourse):
    import plotly.graph_objects as go
    
    trivia_sessions = Trivia.objects.filter(courseID=currentCourse)
    
    # There should be some kind of null check here for an empty 
    # list probably, but nowhere else in the code could I find 
    # another developer doing such a check.

    x = [-2,0,4,6,7]
    y = [q**2-q+3 for q in x]
    trace1 = go.Scatter(x=x, y=y, marker={'color': 'red', 'symbol': 104, 'size': 10},
                        mode="lines",  name='1st Trace')

    layout=go.Layout(title="Test Student (Test Student)", xaxis={'title':'x1'}, yaxis={'title':'x2'})
    figure=go.Figure(data=trace1,layout=layout)

    context_dict['graph'] = figure.to_html()
    context_dict['trivia_sessions'] = zip(trivia_sessions)

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def triviaSessionReviewView(request):

    context_dict, currentCourse = initialContextDict(request)
            
    generate_trivia_review_data(context_dict, currentCourse)

    return render(request, 'Trivia/TriviaSessionReview.html', context_dict)
