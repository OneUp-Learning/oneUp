'''
Created on Apr 11, 2014
Modified on 08/15/2017

'''

from django.shortcuts import render

from Instructors.models import Questions, ResourceTags, QuestionsSkills
from Instructors.models import ChallengesQuestions, Challenges
from Instructors.views.utils import initialContextDict
from Badges.enums import QuestionTypes

from django.contrib.auth.decorators import login_required
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def searchResults(request, context_dict):
        
    qTags = [] 
    selectedTags = []   
    selectedTypes = []
    selectedDifficulties = []
    selectedChallenges = []
    selectedSkills = []
    num_found_questions = 0   
    logger.debug(request.POST)
    print(request.POST.getlist('type'))
    if request.method == 'POST':        
        if 'type' in request.POST:
            # get the list of all checked problem types
            selectedTypes = [qtype for qtype in request.POST.getlist('type')]
        if 'difficulty' in request.POST:
            # get the list of all checked problem difficulties
            selectedDifficulties = [qdificulty for qdificulty in request.POST.getlist('difficulty')]
        if 'skill' in request.POST:
            # get the list of all checked skills
            selectedSkills = [qskill for qskill in request.POST.getlist('skill')]
        if 'challengeID' in request.POST:
            # get the list of all checked challenges
            selectedChallenges = request.POST['challengeID']
            logger.debug(selectedChallenges)
        if 'tags' in request.POST:
            # get the list of all checked problem tags
            selectedTags = json.loads(request.POST['tags'])
            logger.debug("[POST] tags: " + str(selectedTags))

        q_object_type = [] 
        q_object_skills = []
        q_object_tags = []
        q_object_difficulty = []
        q_object_challenge = []
        
        questions = Questions.objects.all()

        #Checking for challenges
        if selectedChallenges:
            
            for question in questions:
                q_challenge_db = ChallengesQuestions.objects.filter(questionID = question, challengeID=int(selectedChallenges))
                #q_challegenames_db = [qc.challengeID.challengeName for qc in q_challenge_db]  
                              
                # Check if the intersection of the two sets of challenge names for this question is not empty
                # We want to return the question if it appears in any of the selected challenges
 
                #if set(selectedChallenges).intersection(set(q_challegenames_db)):
                #if not set(selectedChallenges).isdisjoint(q_challegenames_db):                
                if q_challenge_db.exists():
                    q_object_challenge.append(question)
                      
        else:
            q_object_challenge = questions
                        
        #Checking for skills
        if selectedSkills:
            # Find the skills to which this question is related
            for question in q_object_challenge:
                q_skill_db = QuestionsSkills.objects.filter(questionID = question)
                q_skillnames_db = [qs.skillID.skillName for qs in q_skill_db]                

                # We want to return the question if it is related to any of the selected in the filter form skills
                if not set(selectedSkills).isdisjoint(q_skillnames_db):
                    q_object_skills.append(question)                   
        else:
            q_object_skills = q_object_challenge

        
        # Filtering on question type
        if selectedTypes:
            q_object_type = [q for q in q_object_skills if str(q.type) in selectedTypes]                               
        else:
            q_object_type = q_object_skills
                    
        # Filtering on difficulty
        if selectedDifficulties:
            q_object_difficulty = [q for q in q_object_type if q.difficulty in selectedDifficulties]                                
        else:
            q_object_difficulty = q_object_type
                        
        #Checking for tags
        if selectedTags:
            for question in q_object_difficulty:
                q_tags_db = ResourceTags.objects.filter(questionID = question)
                q_tagnames_db = [t.tagID.tagName for t in q_tags_db]              
                
                if not set(selectedTags).isdisjoint(q_tagnames_db):
                    q_object_tags.append(question)       
        else:
            q_object_tags = q_object_difficulty
                                                                                  
        q_ID = []      
        q_preview = []         
        q_type = []
        q_type_name = []
        q_difficulty = []
        q_challengeId= []
        q_type_displayName = []
        q_position = []
        
        for question in q_object_tags:
 
            #the question satisfies the requirements
            q_ID.append(question.questionID)
            q_preview.append(question.preview)
            q_position.append(num_found_questions)
            
            qtype=question.type
            q_type.append(qtype)
            q_type_name.append(QuestionTypes.questionTypes[qtype]['name'])
            q_type_displayName.append(QuestionTypes.questionTypes[qtype]['displayName'])

            q_difficulty.append(question.difficulty)
            q_challengeId.append((ChallengesQuestions.objects.filter(questionID = question.questionID)[:1].get()).challengeID.challengeID)            
            num_found_questions = num_found_questions + 1 

        #If no results were found then we pass empty=true to the html page
        if not q_ID:
            context_dict['empty'] = 1
        else:  
            context_dict['question_range'] = sorted(list(zip(range(1,num_found_questions+1),q_ID,q_preview,q_type_name,q_type_displayName, q_difficulty, q_position)), key=lambda tup: tup[6])
        
        #if 'challengeID' in request.POST:                                   # 03/05/2015
         #   context_dict['challengeID'] = request.POST['challengeID']
          #  context_dict['challenge'] = True
           # challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))
            #context_dict['challengeName'] = challenge.challengeName    
                
        return context_dict    
        #return render(request,'Instructors/ChallengeQuestionsList.html', context_dict)

