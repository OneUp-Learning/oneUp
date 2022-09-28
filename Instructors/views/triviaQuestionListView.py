'''
Created on December 13, 2021

@author: ismith
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from Instructors.models import Trivia, TriviaAnswer, TriviaQuestion

from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck

def createTriviaQuestionRange(triviaID):
    # Create a range of questions
    question_ids = []
    question_texts = []
    question_types = []
    question_answers = []
    
    TriviaQuestions = TriviaQuestion.objects.filter(triviaID=triviaID).order_by('questionPosition')
    
    for question in TriviaQuestions:
        trivia_question_id = question.questionID
        trivia_question_text = question.questionText
        trivia_question_type = question.questionType
        trivia_answers = []
        
        possible_answers = TriviaAnswer.objects.filter(questionID=trivia_question_id)
        for answer in possible_answers:
            trivia_answers.append({'answerText': answer.answerText, 'isCorrect': answer.isCorrect})
        
        question_ids.append(trivia_question_id)
        question_texts.append(trivia_question_text)
        question_types.append(trivia_question_type)
        question_answers.append(trivia_answers)
        
    return sorted(zip(range(1, len(question_ids) + 1), question_ids, question_texts, question_types, question_answers), key=lambda x: x[0])

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def createTriviaQuestionListView(request):

    context_dict, currentCourse = initialContextDict(request)

    if 'triviaID' in request.GET:   
        trivia = Trivia.objects.get(triviaID=int(request.GET['triviaID']))
    elif 'triviaID' in request.POST:
        trivia = Trivia.objects.get(triviaID=int(request.POST['triviaID']))
        
    context_dict['triviaID'] = trivia
    context_dict["trivia_question_range"] = createTriviaQuestionRange(trivia)
    return render(request, 'Instructors/TriviaQuestionList.html', context_dict)

def batchDeleteTriviaProblems(request, questions):
    context_dict, currentCourse = initialContextDict(request)
    print("Problems:", questions)
    for question in questions:
        delete_question = TriviaQuestion.objects.get(questionID=int(question))
        delete_question.delete()

@login_required
def deleteProblemsButFilterTakenByStudent(request):
    from django.http import JsonResponse
    
    context_dict, currentCourse = initialContextDict(request)

    errorList = []
    response = {}
    
    if request.POST:
        if 'deletion_checkboxes' in request.POST:
            delete_list=str.split(request.POST['deletion_checkboxes'],sep=',')
            errorList = batchDeleteTriviaProblems(request, delete_list)
            response['errorMessages'] = errorList
        return JsonResponse(True)
    return JsonResponse(False)