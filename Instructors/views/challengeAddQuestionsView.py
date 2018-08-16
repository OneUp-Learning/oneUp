'''
Created on May 14, 2014

@author: dichevad
'''
from django.shortcuts import render

from Instructors.models import Challenges, Questions
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def challengeAddQuestionsView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)
        
    if request.POST['challengeID']:
        challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))

        #Get information about questions from the database to send to the TestQuestionForm
        # First get the filters from the http request
  
        leveldiffs = []
        challenges = []
        selectedTypes = []
        
        # get the list of all checked answers
        stypes = request.POST.getlist('selectedType')
        for i in range(0, len(stypes)):
            selectedTypes.append(str(stypes[i]))
            print(str(stypes[i]))
            
        #selectedDifficulties = request.POST.getlist('qdifficulty'+str(i))
#         selectedChallenges = request.POST.getlist('selectedChallenge')

        # get selected tags
#         if request.POST['tags']:
#             tags_csv = request.POST['tags']
#             rtags = tags_csv.split(',')

        q_ID = []      
        q_preview = []         
        q_type = []
        q_challenge = []
        #q_difficulty = []
        q_author = []

        questions = Questions.objects.all()
        for question in questions:
            # check if question satisfies the requirements 
            is_good = False                                              
#             if question.CoursePK == int(request.POST['coursePK'+str(x)]) and  question.TopicPK == int(request.POST['topicPK'+str(x)]): 
#                 is_good = True
                
            # check difficulty
            #if (question.difficulty in selectedDifficulties) and (question.type.typeName in selectedTypes) :
            #print(str(question.type))
            if str(question.type) in selectedTypes :
                is_good = True
            print(str(is_good))    
            
            #POST all tags for these question from the database
#             if request.POST['tags']:
#                 ind = True
#                 q_tags_db = Tags.objects.get(pk=question.questionID)
#                 for rtag in rtags:
#                     if not rtag in q_tags_db:
#                         ind = False
#                 if ind:
#                     is_good = True
            
            # need to add also the course and challenge
            
            if is_good :                            
                #the question satisfies the requirements
                q_ID.append(question.questionID)
                q_preview.append(question.preview)
                q_type.append(question.type)
                #q_difficulty.append(question.difficulty)
                q_author.append(question.author)

            
        context_dict['challengeID'] = challenge.challengeID
        context_dict['question_range'] = zip(range(1,questions.count()+1),q_ID,q_preview,q_type,q_author)        

    return render(request,'Instructors/ChallengeReuseQuestions.html', context_dict)

