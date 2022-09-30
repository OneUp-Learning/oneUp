'''
Created on Oct 23, 2020

@author: ismith
'''
import json
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Trivia, TriviaAnswer, TriviaQuestion
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def CreateTriviaQuestion(request):
    # AJAX Handler for trivia questions
    context_dict, currentCourse = initialContextDict(request)
    
    if request.is_ajax and request.method == "POST":
        json_data = json.loads(request.body)
        question = json_data['question']
        answers = json_data['answers']
        max_points = json_data['max_points']
        triviaID = json_data['triviaID']
        question_type = json_data["question_type"]
        
        if triviaID: 
            trivia = Trivia.objects.get(triviaID=triviaID, courseID=currentCourse)
            if trivia:
                new_question = TriviaQuestion(triviaID=trivia, questionText = question, questionType=question_type, maxPoints=max_points)
                new_question.save()
                for answer in answers:
                    new_answer = TriviaAnswer(questionID=new_question, answerText = answer['text'], isCorrect = answer['isCorrect'])
                    new_answer.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def editTriviaTrueFalseQuestion(request):
    context_dict, currentCourse = initialContextDict(request)
    
    if request.method == "GET":
        if 'triviaID' in request.GET:
            context_dict['triviaID'] = request.GET['triviaID']
            trivia = Trivia.objects.get(triviaID=int(request.GET['triviaID']), courseID=currentCourse)
            if trivia:
                context_dict['trivia'] = trivia
                context_dict['trivia_name'] = trivia.triviaName
                
                if 'questionID' in request.GET:
                    requested_question = TriviaQuestion.objects.get(questionID=int(request.GET['questionID']), triviaID=trivia)
                    if requested_question:
                        context_dict['questionID'] = requested_question.questionID
                        context_dict['questionText'] = requested_question.questionText
                        context_dict['maxPoints'] = requested_question.maxPoints
                        possible_answers = TriviaAnswer.objects.filter(questionID=requested_question)
                        
                        trivia_answerTexts = []
                        trivia_answerCorrect = []
                        for answer in possible_answers:
                            print(answer.answerText)
                            print("correct: ", answer.isCorrect)
                            trivia_answerTexts.append(answer.answerText)
                            trivia_answerCorrect.append(answer.isCorrect)
                        context_dict['answers'] = sorted(zip(range(1, len(trivia_answerTexts) + 1), trivia_answerTexts, trivia_answerCorrect), key=lambda x: x[0])
                        
            return render(request, 'instructors/TriviaTrueFalseForm.html', context_dict)
        
def editTriviaQuestion(request):
    context_dict, currentCourse = initialContextDict(request)
    
    if request.method == "POST" and request.is_ajax:
        json_data = json.loads(request.body)
        if 'triviaID' in json_data:
            triviaID = json_data['triviaID']
            trivia = Trivia.objects.get(triviaID=int(triviaID), courseID=currentCourse)
            if trivia:
                if 'questionID' in json_data:
                    question_id = json_data['questionID']
                    requested_question = TriviaQuestion.objects.get(questionID=int(question_id), triviaID=trivia)
                    if requested_question:
                        question_text = json_data['question']
                        max_points = json_data['max_points']
                        requested_question.questionText = question_text
                        requested_question.maxPoints = max_points
                        requested_question.save()
                        
                        answers = TriviaAnswer.objects.filter(questionID=requested_question)
                        for answer in answers:
                            answer.delete()
                            
                        new_answers = json_data['answers']
                        for answer in new_answers:
                            print(answer)
                            new_answer = TriviaAnswer()
                            new_answer.questionID=requested_question
                            new_answer.answerText = answer['text']
                            new_answer.isCorrect = answer['isCorrect']
                            new_answer.save()
                            print(new_answer.answerText)
                            print(new_answer.isCorrect)
                        return JsonResponse({"success": True})
        return JsonResponse({"success": False})
    return HttpResponseNotFound("<h1>Page not found</h1>")

def editTriviaMultipleAnswerQuestion(request):
    context_dict, currentCourse = initialContextDict(request)
    if request.method == "GET":
        if 'triviaID' in request.GET:
            context_dict['triviaID'] = request.GET['triviaID']
            trivia = Trivia.objects.get(triviaID=int(request.GET['triviaID']), courseID=currentCourse)
            if trivia:
                context_dict['trivia'] = trivia
                context_dict['trivia_name'] = trivia.triviaName
                
                if 'questionID' in request.GET:
                    requested_question = TriviaQuestion.objects.get(questionID=int(request.GET['questionID']), triviaID=trivia)
                    if requested_question:
                        context_dict['questionID'] = requested_question.questionID
                        context_dict['questionText'] = requested_question.questionText
                        context_dict['maxPoints'] = requested_question.maxPoints
                        possible_answers = TriviaAnswer.objects.filter(questionID=requested_question)
                        
                        trivia_answerTexts = []
                        trivia_answerCorrect = []
                        for answer in possible_answers:
                            print(answer.answerText)
                            print("correct: ", answer.isCorrect)
                            trivia_answerTexts.append(answer.answerText)
                            trivia_answerCorrect.append(answer.isCorrect)
                        context_dict['answers'] = sorted(zip(range(1, len(trivia_answerTexts) + 1), trivia_answerTexts, trivia_answerCorrect), key=lambda x: x[0])
                        
    return render(request, 'instructors/TriviaMultipleAnswerForm.html', context_dict)

def deleteTriviaQuestion(request):
    # AJAX Handler for trivia questions
    context_dict, currentCourse = initialContextDict(request)
    
    if request.is_ajax and request.method == "POST":
        if 'triviaId' in request.POST:
            context_dict['triviaId'] = request.POST['triviaId']
            trivia = Trivia.objects.get(triviaID=int(request.POST['triviaId']), courseID=currentCourse)
            if 'questionId' in request.POST:
                questionID = request.POST['questionId']
                question = TriviaQuestion.objects.get(triviaID=trivia, questionID=int(questionID))
                if question:
                    question.delete()
                    return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def performDeletion(request, questions):
    context_dict, currentCourse = initialContextDict(request)
    
    errorList = []
    if 'triviaId' in request.POST:
        trivia = Trivia.objects.get(triviaID=int(request.POST['triviaId']), courseID=currentCourse)
        for question in questions:
            delete_question = TriviaQuestion.objects.get(questionID=int(question), triviaID=trivia)
            if delete_question:
                delete_question.delete()
            else:
                errorList.append(question)
        
    return errorList

@login_required
def deleteTriviaQuestionsBatch(request):
    context_dict, currentCourse = initialContextDict(request)

    errorList = []
    response = {}
    
    if request.POST:
        if 'deletion_checkboxes' in request.POST:
            delete_list=str.split(request.POST['deletion_checkboxes'],sep=',')
            print("Delete List:", delete_list)
            errorList = performDeletion(request, delete_list)
            response['errorMessages'] = errorList
            print(errorList)
            
    return JsonResponse(response)
