'''
Created on November 09, 2017

@author: Oumar
'''

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required,  user_passes_test
from Instructors.models import ChallengesQuestions
from Instructors.views.utils import initialContextDict
from Instructors.lupaQuestion import lupa_available 
from oneUp.decorators import instructorsCheck     

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def reorderChallengeSaveQuestions(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict['lupa_available'] = lupa_available
        
    if request.POST:
        if request.POST['challengeID']:
            challengeId = request.POST['challengeID']
            
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
               
            print("challe question")
            print(challenge_questions)  
            
            for challenge_question in challenge_questions:
                print(challenge_question.questionID.questionID)
                if str(challenge_question.questionID.questionID) in request.POST:
                    challenge_question.questionPosition = request.POST[str(challenge_question.questionID.questionID)]
                    challenge_question.save()
      
    
    return redirect('/oneUp/instructors/challengeQuestionsList?challengeID=' + challengeId)
    
     