'''
Created on Apr 12, 2014

@author: dichevad
'''
from django.shortcuts import redirect
from django.shortcuts import render

from Instructors.models import Challenges, ChallengesQuestions, Questions
from Instructors.views import challengeListView
from Instructors.views.utils import initialContextDict
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge
from Instructors.constants import unassigned_problems_challenge_name

from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck   
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def challengeSaveSelectedQuestions(request):

    context_dict, currentCourse = initialContextDict(request)
    # need to store the information about selected questions in the database   
    if request.POST:
        
        challengeID = request.POST.get('challengeID')
        challenge = Challenges.objects.get(pk=int(challengeID))
        indGraded = challenge.isGraded
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, indGraded)
        selected = request.POST.getlist('selected')
        selectedQuestions = [ int(x) for x in selected ]
        
        # No checbox (question) sellected: return to page displaying the list of questions
        if not selectedQuestions:
            context_dict = makeContextDictForQuestionsInChallenge(challengeID, context_dict)                                                 
            return render(request,'Instructors/ChallengeQuestionsList.html', context_dict)
        
        print("selected list"+str(selectedQuestions))
        print ("max value"+str(max(selectedQuestions)))
        
        # For each question in Selected       
        for i in range(1,int(max(selectedQuestions))+1):
            if i in selectedQuestions:
                chq = ChallengesQuestions()         # a new challenge-question object
                chq.challengeID = challenge 
                chq.points = request.POST.get('points'+str(i))
                if not chq.points:
                    chq.points = 0   
                qID =  request.POST.get('questionID'+str(i)) 
                print(str(qID))  
                chq.questionID = Questions.objects.get(pk=int(qID))            
         
                chq.save();  #Save challenge-question to database                       
            
                #Getting the challenge ID for Unassigned Problems challenge
                chall=Challenges.objects.filter(challengeName=unassigned_problems_challenge_name,courseID=currentCourse)
                for challID in chall:
                    uChallengeID = challID.challengeID
                
                #Checks to see if the question that we adding is in the Unassigned Problems challenge
                #If it is then we delete it from the Unassigned Problems challenge
                if ChallengesQuestions.objects.filter(challengeID= uChallengeID, questionID = qID):
                    question = ChallengesQuestions.objects.filter(challengeID= uChallengeID, questionID = qID)
                    question.delete()

            
    return redirect('/oneUp/instructors/challengeQuestionsList?challengeID=' + challengeID)


