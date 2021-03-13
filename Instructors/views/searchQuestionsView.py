'''
Created on Apr 10, 2014

@author: dichevad
'''
from django.shortcuts import render

from Instructors.models import Challenges, CoursesSkills, CoursesTopics,\
    ChallengesQuestions
from Instructors.views.utils import initialContextDict
from Badges.enums import dict_dict_to_zipped_list
from Instructors.questionTypes import QuestionTypes

from django.contrib.auth.decorators import login_required,  user_passes_test
from oneUp.decorators import instructorsCheck  
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def searchQuestions(request):

    context_dict, currentCourse = initialContextDict(request);  
    
    typename = []      
    tags = []    
    leveldiffs = []
    qchallengeName = []
    qchallengeID = []
    hasParsons = []
    qdifficulty = []
    qskill = []
    ctopicID = []
    ctopicName = []
    qdifficulties = ['Easy', 'Medium', 'Hard']
    

    # Get information for question types to display on the search page       
    questionTypesObjects= dict_dict_to_zipped_list(QuestionTypes.questionTypes,['index','displayName'])
     
    # information about the level of difficulty
    num_qdifficulties = len(qdifficulties)
    for i in range(0, num_qdifficulties):
        qdifficulty.append(qdifficulties[i])
        
    # Get course topics 
    c_topics = CoursesTopics.objects.filter(courseID = currentCourse)
    for ct in c_topics:
        ctopicName.append(ct.topicID.topicName)
        ctopicID.append(ct.topicID.topicID)  
    
    context_dict['topic_range'] = zip(range(1, c_topics.count() + 1), ctopicID, ctopicName)

    # Get skills from the DB
    c_skills = CoursesSkills.objects.filter(courseID = currentCourse)
    for cs in c_skills:
        qskill.append(cs.skillID.skillName) 
    
    context_dict['skill_range'] = zip(range(1, c_skills.count() + 1), qskill)
            
    # Get challenges from the DB
    challenges = Challenges.objects.filter(courseID=currentCourse)
    for chall in challenges:
        qchallengeName.append(chall.challengeName)
        qchallengeID.append(chall.challengeID)
        
    context_dict['qtypes_range'] = questionTypesObjects
    context_dict['qdifficulty_range'] = zip(range(1, num_qdifficulties + 1), qdifficulty)
    zipped = zip(range(1, num_challenges + 1), qchallengeName, qchallengeID)
    context_dict['challenge_range'] = sorted(zipped, key=lambda x: x[1].lower())
    print('context_dict')
    print(qchallengeName)
    print(qchallengeID)
    
    if 'challengeID' in request.GET:         
        context_dict['challenge'] = True
        context_dict['challengeID'] = request.GET['challengeID']
        challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
        context_dict['challengeName'] = challenge.challengeName
        #checks if serious for Parson's warning
        if challenge.isGraded:
            context_dict['isSerious']='serious'
            
    return render(request,'Instructors/SearchQuestions.html', context_dict)
        
        
