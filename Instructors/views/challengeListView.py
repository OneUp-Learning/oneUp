'''
Created on Apr 7, 2014
Last updated 07/15/2017

@author: dichevad
'''
from django.shortcuts import render

from Instructors.models import Courses, Challenges, ChallengesQuestions, Topics, CoursesTopics, ChallengesTopics
from Instructors.constants import  unspecified_topic_name, default_time_str
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck
from Badges.events import register_event
from Badges.enums import Event
from Instructors.questionTypes import QuestionTypes
from Students.models import StudentRegisteredCourses
from time import strftime

from Instructors.constants import unassigned_problems_challenge_name


def makeContextDictForQuestionsInChallenge(challengeId, context_dict):    # 02/28/15
    
    questionObjects= []
    q_ID = []      #PK for existing answers6
    q_preview = []             
    q_type_name = []
    q_type_displayName = []
    q_difficulty = []
    q_position = []

    # If questionId is specified then we load for editing.
    challenge = Challenges.objects.get(pk=int(challengeId))    
    context_dict['challenge'] = True
    context_dict['challengeID'] = challenge.challengeID
    context_dict['challengeName'] = challenge.challengeName
                      
    # Get the questions for this challenge 
    challenge_questions = ChallengesQuestions.objects.filter(challengeID=int(challengeId))
         
    for challenge_question in challenge_questions:
        questionObjects.append(challenge_question.questionID)
        q_position.append(challenge_question.questionPosition)
 
    for question in questionObjects:
        q_ID.append(question.questionID)
        q_preview.append(question.preview)
        q_type=question.type
        q_type_name.append(QuestionTypes.questionTypes[q_type]['name'])
        q_type_displayName.append(QuestionTypes.questionTypes[q_type]['displayName'])
        q_difficulty.append(question.difficulty)
        
    
                
        
    # The range part is the index numbers.
    context_dict['question_range'] = sorted(list(zip(range(1,len(questionObjects)+1),q_ID,q_preview,q_type_name,q_type_displayName, q_difficulty, q_position )), key=lambda tup: tup[6])
    
    return context_dict


def makeContextDictForChallengeList(context_dict, courseId, indGraded):
   
    chall_ID = []      
    chall_Name = []         
    #chall_Category = []
    #chall_Difficulty = []
    chall_visible = []
    start_Timestamp = []
    end_Timestamp = []
    chall_due_date = []
    chall_Position = []
    UnassignID = 0
    
    chall=Challenges.objects.filter(challengeName=unassigned_problems_challenge_name,courseID=courseId)
    for challID in chall:
        UnassignID = challID.challengeID   
        
    if indGraded:    
        challenges = Challenges.objects.filter(courseID=courseId, isGraded=True)
    else:
        challenges = Challenges.objects.filter(courseID=courseId, isGraded=False)
    
    for item in challenges:
        if item.challengeID != UnassignID:
            chall_ID.append(item.challengeID) #pk
            chall_Name.append(item.challengeName)
            chall_Position.append(item.challengePosition)
            #chall_Category.append(item.challengeCategory)
            #chall_Difficulty.append(item.challengeDifficulty)
            if item.isVisible:
                chall_visible.append("Visible")
            else:
                chall_visible.append("Not Visible")
                    
            if item.startTimestamp.strftime("%Y") < ("2900"):
                start_Timestamp.append(item.startTimestamp)
            else:
                start_Timestamp.append("")
            
            if item.endTimestamp.strftime("%Y") < ("2900"):
               
                end_Timestamp.append(item.endTimestamp)
            else:
                end_Timestamp.append("")

            chall_due_date.append(item.dueDate)
               
    # The range part is the index numbers.
    context_dict['challenge_range'] = sorted(list(zip(range(1,challenges.count()+1),chall_ID,chall_Name,chall_visible,start_Timestamp,end_Timestamp,chall_due_date, chall_Position)), key=lambda tup: tup[7])  ##,chall_Category
    return context_dict


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def challengesList(request):
    
    context_dict, currentCourse = initialContextDict(request)
        
    if 'warmUp' in request.GET:
            warmUp = 1
            context_dict['warmUp']= 1
    else:
        warmUp = 0    

    
    if warmUp == 1:
        context_dict = makeContextDictForChallengeList(context_dict, currentCourse, False)
    else:
        context_dict = makeContextDictForChallengeList(context_dict, currentCourse, True)
    
    topic_ID = []      
    topic_Name = [] 
    topic_Pos = []     
    challenges_count = []   
    all_challenges_for_topic = []
    hasUnspecified_topic = False

    course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
    for ct in course_topics:
        
        tID = ct.topicID.topicID
        tName = Topics.objects.get(pk=tID).topicName
        if not tName == unspecified_topic_name:   # leave challenges with unspecified topic for last        
            topic_ID.append(tID)
            topic_Name.append(tName)
            topic_Pos.append(ct.topicPos)
            topic_challenges = challengesForTopic(ct.topicID, currentCourse, isGraded=True) 
            challenges_count.append(len(list(topic_challenges)))
            all_challenges_for_topic.append(topic_challenges)
        else:
            unspecified_topic = ct.topicID 
            hasUnspecified_topic=True  
           
    # Add the challenges with unspecified topic at the end
    if hasUnspecified_topic:
        topic_ID.append(unspecified_topic.topicID)
        topic_Name.append("Miscellaneous")
        if topic_Pos: 
            max_pos = max(topic_Pos)
        else:
            max_pos = 0
        topic_Pos.append(max_pos+1) 
        topic_challenges = challengesForTopic(unspecified_topic, currentCourse, isGraded=True)
        challenges_count.append(len(list(topic_challenges)))
        all_challenges_for_topic.append(topic_challenges)
                    
    context_dict['topic_range'] = sorted(list(zip(range(1,course_topics.count()+1),topic_ID,topic_Name,topic_Pos,challenges_count,all_challenges_for_topic)),key=lambda tup: tup[3])
            
    return render(request,'Instructors/ChallengesList.html', context_dict)
    

def challengesForTopic(topic, currentCourse, isGraded=False):

    chall_ID = []  
    chall_Name = [] 
    #chall_Difficulty = []
    chall_visible = []
    chall_position = []
    if isGraded:
        start_Timestamp = []
        end_Timestamp = []
        chall_due_date = []
        chall=Challenges.objects.filter(challengeName=unassigned_problems_challenge_name,courseID=currentCourse)
        for challID in chall:
            UnassignID = challID.challengeID  
        challenge_topics = ChallengesTopics.objects.filter(topicID=topic)
        
        if challenge_topics:           
            for challt in challenge_topics:
                if Challenges.objects.filter(challengeID=challt.challengeID.challengeID, isGraded=True, courseID=currentCourse):
                    print("Topics: {}".format(challenge_topics))
                    print(topic)
                    item =  challt.challengeID
                    if item.challengeID != UnassignID:
                        chall_ID.append(item.challengeID)
                        chall_Name.append(item.challengeName)
                        chall_position.append(item.challengePosition)

                        if item.isVisible:
                            chall_visible.append("Visible")
                        else:
                            chall_visible.append("Not Visible")
                                
                        if item.startTimestamp.strftime("%Y") < ("2900"):
                            start_Timestamp.append(item.startTimestamp)
                        else:
                            start_Timestamp.append("")
                        
                        if item.endTimestamp.strftime("%Y") < ("2900"):
                        
                            end_Timestamp.append(item.endTimestamp)
                        else:
                            end_Timestamp.append("")

                        chall_due_date.append(item.dueDate)
                    
        return sorted(list(zip(range(1,challenge_topics.count()+1),chall_ID,chall_Name,chall_visible,start_Timestamp,end_Timestamp,chall_due_date, chall_position)), key=lambda tup: tup[7])
    else:
        challenge_topics = ChallengesTopics.objects.filter(topicID=topic)
        if challenge_topics:           
            for challt in challenge_topics:
                if Challenges.objects.filter(challengeID=challt.challengeID.challengeID, isGraded=isGraded, courseID=currentCourse):
                    chall_ID.append(challt.challengeID.challengeID)
                    chall_Name.append(challt.challengeID.challengeName)
                    #chall_Difficulty.append(challt.challengeID.challengeDifficulty)
                    chall_position.append(challt.challengeID.challengePosition)
                    if challt.challengeID.isVisible:
                        chall_visible.append('Visible')
                    else:
                        chall_visible.append('Not Visible')
                    
        return sorted(list(zip(range(1,challenge_topics.count()+1),chall_ID,chall_Name,chall_visible,chall_position)), key=lambda tup: tup[4])

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def warmUpChallengeList(request):
    
    # Warm challenged will be grouped by course topics
    
    context_dict, currentCourse = initialContextDict(request)

    topic_ID = []      
    topic_Name = [] 
    topic_Pos = []     
    challenges_count = []   
    all_challenges_for_topic = []
    hasUnspecified_topic = False

    course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
    for ct in course_topics:
        
        tID = ct.topicID.topicID
        tName = Topics.objects.get(pk=tID).topicName
        if not tName == unspecified_topic_name:   # leave challenges with unspecified topic for last        
            topic_ID.append(tID)
            topic_Name.append(tName)
            topic_Pos.append(ct.topicPos)
            topic_challenges = challengesForTopic(ct.topicID, currentCourse) 
            challenges_count.append(len(list(topic_challenges)))
            all_challenges_for_topic.append(topic_challenges)
        else:
            unspecified_topic = ct.topicID 
            hasUnspecified_topic=True  
           
    # Add the challenges with unspecified topic at the end
    if hasUnspecified_topic:
        topic_ID.append(unspecified_topic.topicID)
        topic_Name.append("Miscellaneous")
        if topic_Pos: 
            max_pos = max(topic_Pos)
        else:
            max_pos = 0
        topic_Pos.append(max_pos+1) 
        topic_challenges = challengesForTopic(unspecified_topic, currentCourse)
        challenges_count.append(len(list(topic_challenges)))
        all_challenges_for_topic.append(topic_challenges)
                    
    context_dict['topic_range'] = sorted(list(zip(range(1,course_topics.count()+1),topic_ID,topic_Name,topic_Pos,challenges_count,all_challenges_for_topic)),key=lambda tup: tup[3])

    return render(request,'Instructors/ChallengesWarmUpList.html', context_dict)
    
#compares current time with the endTimestamp of each challenge
#if the current time exceeds the endTimestamp, the challenge is made unavailable
def disableExpiredChallenges(request):
    challenges = Challenges.objects.all()
    currentTime = strftime("%Y-%m-%d %H:%M:%S")
    
    for challenge in challenges:
        if (currentTime > challenge.endTimestamp.strftime("%Y-%m-%d %H:%M:%S")):
            #Need to add code to disable the challenge from being taken
            
            #ONLY AWARD BADGE ON CHALLENGE EXPIRATION

            registeredStudents = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])

            for student in registeredStudents:
                register_event(Event.challengeExpiration, request, student.studentID, challenge.challengeID)
                print("Registered Event: Challenge Expiration Event, Student: " + str(student.studentID) + ", Challenge: " + str(challenge.challengeID))
            
