'''
Created on April 8, 2020

@author: GGM
'''
import enum
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Students.models import Student, StudentAnswerHints
from Students.views.utils import studentInitialContextDict
from Instructors.models import ChallengesQuestions, Questions
from Badges.models import CourseConfigParams

@login_required
def flashCardsView(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
        
    context_dict['weakHint'] = ccparams.weightBasicHint
    context_dict['strongHint'] = ccparams.weightStrongHint
    return render(request,'Students/FlashCards.html',context_dict)    
@login_required
def hintInfoView(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
        
    context_dict['weakHint'] = ccparams.weightBasicHint
    context_dict['strongHint'] = ccparams.weightStrongHint
    return render(request,'Students/HintsInfo.html',context_dict)

@login_required
def hintsUsed(request):
    ##this is used to track how many times the student clicks class average
    ##we use ajax to track the information, otherwise they'd get the page refreshed on them
    ##and it would be "wrong".
    
    context_dict, currentCourse = studentInitialContextDict(request)

    hints = {}
    response = {}
    #dict['hintsUsed'] = {}

    if request.POST:
        student = Student.objects.get(user=request.user)
        if 'challengeQuestionID' in request.POST:
            hintType = convertToEnum(request.POST['type'])
            studentHintObjectID = createStudentHint(request.POST['challengeQuestionID'], hintType, student).studentAnswerHintsID
            hint = obtainHint(request.POST['challengeQuestionID'], hintType)
            return JsonResponse( 
                {
                "hintID" : studentHintObjectID ,
                "hint": hint
                }
            )

def createStudentHint(challengeQuestionsID, typeOfHint, student):
    #first determine if the hint already exists
    studentAnswerHint = StudentAnswerHints.objects.filter(challengeQuestionID=challengeQuestionsID, studentID=student, studentChallengeQuestionID__isnull=True)

    if studentAnswerHint.exists():
        studentAnswerHint = StudentAnswerHints.objects.get(challengeQuestionID=challengeQuestionsID, studentID=student, studentChallengeQuestionID__isnull=True)
    else:
        studentAnswerHint = StudentAnswerHints()
    studentAnswerHint.challengeQuestionID = int(challengeQuestionsID)
    studentAnswerHint.studentID = student
    if(typeOfHint == HintType.basic):
        studentAnswerHint.usedBasicHint = True
    if (typeOfHint == HintType.strong):
        studentAnswerHint.usedStrongHint = True
    studentAnswerHint.save()
    return studentAnswerHint

def obtainHint(challengeQuestionsID, typeOfHint):
    challengeQuestion = ChallengesQuestions.objects.get(pk=int(challengeQuestionsID))
    question = challengeQuestion.questionID
    if(typeOfHint == HintType.basic):
        return question.basicHint
    if(typeOfHint == HintType.strong):
        return question.strongHint

def convertToEnum(typeOfHint):
    typeOfHint = int(typeOfHint)
    if(typeOfHint == 0):
        return HintType.basic
    if(typeOfHint == 1):
        return HintType.strong

class HintType(enum.Enum):
   basic = 0
   strong = 1