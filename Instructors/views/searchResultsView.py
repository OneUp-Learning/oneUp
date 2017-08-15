'''
Created on Apr 11, 2014

@author: dichevad
'''

from django.shortcuts import render

from Instructors.models import Questions, ResourceTags, Courses
from Instructors.models import ChallengesQuestions, Challenges
from Badges.enums import QuestionTypes

from django.contrib.auth.decorators import login_required

@login_required


def searchResults(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'

    qTags = [] 
    qTypes = []    
    qChallenges = []
    qDifficulties = []  
    selectedTags = []   
    selectedTypes = []
    selectedDifficulties = []
    selectedChallenges = []
    num_found_questions = 0
    #selectedChallenge = []
    
      
    if request.POST:        

        # get the list of all checked problem types
        qTypes = request.POST.getlist('selectedType')
        for i in range(0, len(qTypes)):
            selectedTypes.append(str(qTypes[i]))
            
        # get the list of all checked problem difficulties
        qDifficulties = request.POST.getlist('selectedDifficulty')
        for i in range(0, len(qDifficulties)):
            selectedDifficulties.append(str(qDifficulties[i]))
            
        # get the list of all checked challenges
        qChallenges = request.POST.getlist('selectedChallenge')
        for i in range(0, len(qChallenges)):
            selectedChallenges.append(str(qChallenges[i]))
            
            
        # get the list of all checked problem tags
        if request.POST['tags']:
            qTags = request.POST['tags']   
            selectedTags = [x.strip() for x in qTags.split(',')]
            
        q_object_type = []      
        q_object_tags = []
        q_object_difficulty = []
        q_object_challenge = []
        q_object = []
        
        questions = Questions.objects.all()
        
        #Checking for question type
        if qTypes:
            for question in questions:
                if str(question.type) in selectedTypes:
                    q_object_type.append(question)
                    
        else:
            q_object_type = questions
                    
        #Checking for difficulty
        if qDifficulties:
            for question in q_object_type:
                if (question.difficulty in selectedDifficulties):
                    q_object_difficulty.append(question)
                    
        else:
            q_object_difficulty = q_object_type
                        
        #Checking for challenges
        if qChallenges:
            for question in q_object_difficulty:
                q_challenge_db = ChallengesQuestions.objects.filter(questionID = question)
                for qc in q_challenge_db:
                    q_challegenames_db = []
                    q_challegenames_db.append(qc.challengeID.challengeName)                                              
                    if sublistExists(qChallenges, q_challegenames_db):
                        q_object_challenge.append(question)  
        else:
            q_object_challenge = q_object_difficulty
                
        #Checking for tags
        if selectedTags:
            for question in q_object_challenge:
                q_tags_db = ResourceTags.objects.filter(questionID = question)
                for t in q_tags_db:
                    q_tagnames_db = []
                    q_tagnames_db.append(t.tagID.tagName) 

                    print(q_tagnames_db)
                    if sublistExists (selectedTags, q_tagnames_db):
                        q_object_tags.append(question)       
        else:
            q_object_tags = q_object_challenge
                
                                                                  
        q_ID = []      
        q_preview = []         
        q_type = []
        q_type_name = []
        q_difficulty = []
        q_challenge = []
        q_challengeId= []
        
        for question in q_object_tags:
        #the question satisfies the requirements
            q_ID.append(question.questionID)
            q_preview.append(question.preview)
            
            #q_type.append(question.type)
            qtype=question.type
            q_type.append(qtype)
            q_type_name.append(QuestionTypes.questionTypes[qtype]['displayName'])

            q_difficulty.append(question.difficulty)
            q_challengeId.append((ChallengesQuestions.objects.filter(questionID = question.questionID)[:1].get()).challengeID.challengeID)            
            num_found_questions = num_found_questions + 1 

        #If no results were found then we pass empty true to html page.
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
        
def sublistExists(list1,list2):
    return set(list1).issubset(set(list2))
