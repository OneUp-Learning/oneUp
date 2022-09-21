'''
Created on Oct 23, 2019

@author: cmickle
'''
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Trivia, TriviaAnswer, TriviaQuestion
from Instructors.views import utils
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def CreateTriviaQuestion(request):
    # AJAX Handler for trivia questions
    # context_dict, currentCourse = utils.initialContextDict(request)
    
    if request.POST:
        json_data = json.loads(request.BODY)
        question = json_data['question']
        answers = json_data['answers']
        question_type = json_data['question_type']
        triviaID = json_data['triviaID']
        
        if triviaID:
            trivia = Trivia.objects.get(triviaID=triviaID)
            if trivia:
                new_question = TriviaQuestion(triviaID=triviaID, questionType=question_type)
            
                new_question.save()
                for answer in answers:
                    new_answer = TriviaAnswer(questionID=new_question.questionID, answerText = answer.text, isCorrect = answer.isCorrect)
                    new_answer.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})
