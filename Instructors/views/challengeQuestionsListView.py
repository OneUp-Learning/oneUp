from django.template import RequestContext
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Challenges, Courses, CoursesSkills
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge
from Instructors.views.searchResultsView import searchResults
from Instructors.views.utils import initialContextDict
from Instructors.lupaQuestion import lupa_available
from Instructors.constants import unassigned_problems_challenge_name

from Badges.enums import QuestionTypes, dict_dict_to_zipped_list

import logging

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
        if challenge.challengeName != "Unassigned Problems":
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
def challengeQuestionsListView(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict['lupa_available'] = lupa_available
        
    if 'challengeID' in request.POST or 'challengeID' in request.GET:   
        challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))    
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
            context_dict["unassign"]= 1
            context_dict['serious'] = False
            context_dict['warmUp'] = False
        else:
            if challenge.isGraded:
                context_dict['serious'] = True
            else:
                context_dict['warmUp'] = True
        context_dict['challenge'] = True
        context_dict['challengeID'] = request.GET['challengeID']
        context_dict['challengeName'] = challenge.challengeName
                                 
    if 'problems' in request.GET or 'problems' in request.POST:
        context_dict["unassign"]= 1   

    context_dict = makeContextDictForSearch(context_dict, currentCourse)

    if request.method == 'POST':
        context_dict = searchResults(request, context_dict, currentCourse)
        
    else:
        
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

  

