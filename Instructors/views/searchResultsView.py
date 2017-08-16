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

@login_required


def searchResults(request):
        
    context_dict, currentCourse = initialContextDict(request);        

    qTags = [] 
    selectedTags = []   
    selectedTypes = []
    selectedDifficulties = []
    selectedChallenges = []
    selectedSkills = []
    num_found_questions = 0   
      
    if request.POST:        

        # get the list of all checked problem types
        selectedTypes = [qtype for qtype in request.POST.getlist('selectedType')]
            
        # get the list of all checked problem difficulties
        selectedDifficulties = [qdificulty for qdificulty in request.POST.getlist('selectedDifficulty')]
 
        # get the list of all checked skills
        selectedSkills = [qskill for qskill in request.POST.getlist('selectedSkills')]
           
        # get the list of all checked challenges
        selectedChallenges = [qchallenge for qchallenge in request.POST.getlist('selectedChallenge')]
            
        # get the list of all checked problem tags
        if request.POST['tags']:
            qTags = request.POST['tags']   
            selectedTags = [x.strip() for x in qTags.split(',')]
            
        q_object_type = [] 
        q_object_skills = []
        q_object_tags = []
        q_object_difficulty = []
        q_object_challenge = []
        
        questions = Questions.objects.all()

        #Checking for challenges
        if selectedChallenges:
            
            for question in questions:
                q_challenge_db = ChallengesQuestions.objects.filter(questionID = question)
                q_challegenames_db = [qc.challengeID.challengeName for qc in q_challenge_db]  
                              
                # Check if the intersection of the two sets of challenge names for this question is not empty
                # We want to return the question if it appears in any of the selected challenges
 
                #if set(selectedChallenges).intersection(set(q_challegenames_db)):
                if not set(selectedChallenges).isdisjoint(q_challegenames_db):                
                    q_object_challenge.append(question)
                      
        else:
            q_object_challenge = questions
            
        print(selectedChallenges)
            
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
        
        for question in q_object_tags:
 
            #the question satisfies the requirements
            q_ID.append(question.questionID)
            q_preview.append(question.preview)
            
            qtype=question.type
            q_type.append(qtype)
            q_type_name.append(QuestionTypes.questionTypes[qtype]['displayName'])

            q_difficulty.append(question.difficulty)
            q_challengeId.append((ChallengesQuestions.objects.filter(questionID = question.questionID)[:1].get()).challengeID.challengeID)            
            num_found_questions = num_found_questions + 1 

        #If no results were found then we pass empty=true to the html page
        if not q_ID:
            context_dict['empty'] = 1
            
        # The range part is the index numbers.
        context_dict['question_range'] = zip(range(1,num_found_questions+1),q_ID,q_preview,q_type,q_type_name,q_difficulty,q_challengeId)
        
        if 'challengeID' in request.POST:                                   # 03/05/2015
            context_dict['challengeID'] = request.POST['challengeID']
            context_dict['challenge'] = True
            challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))
            context_dict['challengeName'] = challenge.challengeName            
            return render(request,'Instructors/ChallengeReuseQuestions.html', context_dict)
        else:
            return render(request,'Instructors/QuestionsList.html', context_dict)

