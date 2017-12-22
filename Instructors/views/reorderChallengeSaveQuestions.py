'''
Created on November 09, 2017

@author: Oumar
'''

from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import ChallengesQuestions
from Instructors.lupaQuestion import lupa_available 

@login_required
def reorderChallengeSaveQuestions(request):
 
    context_dict = { }
    context_dict['lupa_available'] = lupa_available
        
    if request.POST:
        if request.POST['challengeID']:
            challengeId = request.POST['challengeID']
            print("challengeID")
            print(challengeId)
            
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
               
            print(challenge_questions)  
            
            for challenge_question in challenge_questions:
                print(challenge_question.questionID.questionID)
                challenge_question.questionPosition = request.POST[str(challenge_question.questionID.questionID)]
                challenge_question.save()
                
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    return redirect('/oneUp/instructors/challengeQuestionsList?challengeID=' + challengeId)
    
     