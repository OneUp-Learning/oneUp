from django.urls import path
from django.conf.urls import url
from django.shortcuts import redirect

from Trivia.views.triviaHomeView import triviaHomeView
from Instructors.views.deleteView import deleteTrivia
from Instructors.views.reorderViews import reorderTriviaQuestions
from Trivia.views.triviaDashboardView import createTriviaDashboard
from Trivia.views.triviaSessionCreateView import triviaSessionCreateView
from Trivia.views.triviaQuestionListView import createTriviaQuestionListView
from Trivia.views.triviaSessionReviewView import triviaSessionReviewView
from Trivia.views.TriviaQuestionCreateView import CreateTriviaQuestion, deleteTriviaQuestion, deleteTriviaQuestionsBatch, editTriviaMultipleAnswerQuestion, editTriviaQuestion, editTriviaTrueFalseQuestion

from Trivia.views.triviaApi import DoSomething

urlpatterns = [
    url(r'^triviaHome', triviaHomeView),
    url(r'^TriviaDashboard', createTriviaDashboard),
    url(r'^TriviaSessionSetup/?$', triviaSessionCreateView), 
    url(r'^TriviaQuestionList/?$', createTriviaQuestionListView),
    url(r'^removeQuestionTriviaBatch/?$', deleteTriviaQuestionsBatch),
    url(r'^deleteSingleTriviaQuestion/?$', deleteTriviaQuestion),
    url(r'^deleteTrivia/?$', deleteTrivia),
    url(r'^reorderTriviaQuestions/?$', reorderTriviaQuestions),
    url(r'^TriviaSessionReview/?$', triviaSessionReviewView),
    url(r'^createTriviaQuestion/?$', CreateTriviaQuestion),
    url(r'^TriviaTrueFalseForm/?$', editTriviaTrueFalseQuestion),
    url(r'^editTriviaQuestion/?$', editTriviaQuestion),
    url(r'^TriviaMultipleAnswerForm/?$', editTriviaMultipleAnswerQuestion),
    
    # Trivia API stuff
    url(r'^api/trivia/getTriviaQuestions/?$', DoSomething),
]