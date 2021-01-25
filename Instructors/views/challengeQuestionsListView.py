from django.template import RequestContext
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Challenges, Courses, CoursesSkills, ChallengesQuestions, Questions
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge
from Instructors.views.searchResultsView import searchResults
from Instructors.views.utils import initialContextDict
from Instructors.lupaQuestion import lupa_available
from Instructors.constants import unassigned_problems_challenge_name
from Students.models import StudentChallengeQuestions

from Badges.enums import dict_dict_to_zipped_list
from Instructors.questionTypes import QuestionTypes

import logging
from oneUp.decorators import instructorsCheck

logger = logging.getLogger(__name__)

def makeContextDictForSearch(context_dict, currentCourse):
    qchallenge = []
    qskill = []
    qdifficulty = ['Easy', 'Medium', 'Hard']
     
    # Get skills from the DB
    c_skills = CoursesSkills.objects.filter(courseID = currentCourse)
    for cs in c_skills:
        qskill.append(cs.skillID.skillName)    
            
    # Get challenges from the DB
    challenges = Challenges.objects.filter(courseID=currentCourse)
    for challenge in challenges:
        if challenge.challengeName != unassigned_problems_challenge_name:
            qchallenge.append(challenge.challengeName)
    
    
    
    
    if len(c_skills) > 0:
        context_dict['has_skills'] = True
    if len(qdifficulty) > 0:
        context_dict['has_difficulty'] = True
    if len(qchallenge) > 0:
        context_dict['has_challenges'] = True

    context_dict['skill_range'] = zip(range(1, len(c_skills) + 1), qskill)
    context_dict['qtypes_range'] = dict_dict_to_zipped_list(QuestionTypes.questionTypes,['index','displayName'])
    context_dict['qdifficulty_range'] = zip(range(1, len(qdifficulty) + 1), qdifficulty)
    context_dict['challenge_range'] = zip(range(1, len(qchallenge) + 1), qchallenge)    

    return context_dict

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def challengeQuestionsListView(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict['lupa_available'] = lupa_available
        
    if request.GET:
        if 'challengeID' in request.GET:   
            challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
            
            currentChallenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
            isRandomized = currentChallenge.isRandomized 
            context_dict['isRandomized'] = isRandomized    
            if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
                context_dict["unassign"]= 1
                context_dict['serious'] = False
                context_dict['warmUp'] = False
            else:
                if challenge.isGraded:
                    context_dict['serious'] = True
                else:
                    context_dict['warmUp'] = True
                    if challenge.isTeamChallenge:
                        context_dict['teamChallenge'] = True
            context_dict['challenge'] = True
            context_dict['challengeID'] = request.GET['challengeID']
            context_dict['challengeName'] = challenge.challengeName

        if 'problems' in request.GET:
            context_dict["unassign"]= 1
            chall=Challenges.objects.filter(challengeName=unassigned_problems_challenge_name,courseID=currentCourse)
            challengeID = None
            for challID in chall:
                challengeID = (str(challID.challengeID)) 
            if challengeID == None:
                context_dict['question_range'] = None
            else:
                context_dict = makeContextDictForQuestionsInChallenge(challengeID, context_dict)      
        else:
            context_dict = makeContextDictForQuestionsInChallenge(request.GET['challengeID'], context_dict)

    return render(request,'Instructors/ChallengeQuestionsList.html', context_dict)

def makeSureTheresNoStudentsUsingThatProblem(problem):
    isAstudentUsingTheProblem = True
    print("len(StudentChallengeQuestions.objects.filter(challengeQuestionID=int(problem)))", len(StudentChallengeQuestions.objects.filter(challengeQuestionID=int(problem))))
    if(len(StudentChallengeQuestions.objects.filter(challengeQuestionID=int(problem))) == 0):
        isAstudentUsingTheProblem = False
    return isAstudentUsingTheProblem

def performDeletion(problems):
    errorList = []
    for problem in problems:
        challengeQuestion = ChallengesQuestions.objects.get(questionID=int(problem))
        if makeSureTheresNoStudentsUsingThatProblem(problem):
            errorList.append("Error: Student data found for problem: "+ challengeQuestion.questionID.preview)
        else:
            question = Questions.objects.get(questionID=int(problem))
            question.delete()
            challengeQuestion.delete()
        
    return errorList
@login_required
def deleteProblemsButFilterTakenByStudent(request):
    ##this is used to track how many times the student clicks class average
    ##we use ajax to track the information, otherwise they'd get the page refreshed on them
    ##and it would be "wrong".
    from django.http import JsonResponse
    
    context_dict, currentCourse = initialContextDict(request)
    context_dict['lupa_available'] = lupa_available

    errorList = []
    response = {}
    
    if request.POST:
        if 'deletion_checkboxes' in request.POST:
            delete_list=str.split(request.POST['deletion_checkboxes'],sep=',')
            errorList = performDeletion(delete_list)
            response['errorMessages'] = errorList
            
    return JsonResponse(response)

