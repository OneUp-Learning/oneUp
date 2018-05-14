'''
Created on Apr 11, 2014
Modified on 08/15/2017
Modified on 26/01/2018

'''

from django.shortcuts import render

from Instructors.models import Questions, ResourceTags, QuestionsSkills
from Instructors.models import ChallengesQuestions, ChallengesTopics, Challenges
from Instructors.views.utils import initialContextDict
from Badges.enums import QuestionTypes

from django.contrib.auth.decorators import login_required
import json

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

        # get the list of all checked course topics
        selectedTopics = [ctopic for ctopic in request.POST.getlist('selectedTopic')]
 
        # get the list of all checked problem types
        selectedTypes = [qtype for qtype in request.POST.getlist('selectedType')]
           
        # get the list of all checked problem difficulties
        selectedDifficulties = [qdificulty for qdificulty in request.POST.getlist('selectedDifficulty')]
 
        # get the list of all checked skills
        selectedSkills = [qskill for qskill in request.POST.getlist('selectedSkills')]
           
        # get the list of all checked challenges
        selectedChallenges = [qchallengeID for qchallengeID in request.POST.getlist('selectedChallenges')]
  
        # get the list of all checked problem tags
        if request.POST['tags']:
            tags = json.loads(request.POST['tags'])
            selectedTags = [tag['tag'] for tag in tags]

        #q_object_topic = []             
        q_object_type = [] 
        q_object_skills = []
        q_object_tags = []
        q_object_difficulty = []
        q_object_challenge = []           
        
        #Checking for topics
        if selectedTopics:
            #get all challenges for these topics and all their questions
            for topic in selectedTopics: 
                topicChallenges = []              
                t_challs = ChallengesTopics.objects.filter(topicID=int(topic)) # get all challenges for this topic

                for chall in t_challs:
                    if chall.challengeID.courseID == currentCourse:
                        topicChallenges.append(chall.challengeID.challengeID)

                # get the questions for this challenge
                for challenge in topicChallenges:
                    #get all problems for challenge
                    chall_questions = ChallengesQuestions.objects.filter(challengeID=challenge)

                    for chall_question in chall_questions:
                        if chall_question.questionID not in q_object_challenge:
                            q_object_challenge.append(chall_question.questionID)


        # If neither challenges or topics are selected, take all challenges
        if not selectedChallenges and not selectedTopics:
            courseChallenges = Challenges.objects. filter(courseID=currentCourse) # get all challenges for this course
            for chall in courseChallenges:
                selectedChallenges.append(chall.challengeID)
   
        for challenge in selectedChallenges:
            #get all problems
            chall_questions = ChallengesQuestions.objects.filter(challengeID=int(challenge))
            for chall_question in chall_questions:
                if chall_question.questionID not in q_object_challenge:
                    q_object_challenge.append(chall_question.questionID)
        
        print(q_object_challenge)                    
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

