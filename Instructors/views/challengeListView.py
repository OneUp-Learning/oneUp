'''
Created on Apr 7, 2014
Last updated 07/15/2017

@author: dichevad
'''
from time import strftime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from Badges.enums import Event
from Badges.events import register_event
from Instructors.constants import (unassigned_problems_challenge_name,
                                   unspecified_topic_name)
from Instructors.models import (Challenges, ChallengesQuestions,
                                ChallengesTopics, Courses, CoursesTopics,
                                Topics)
from Instructors.questionTypes import QuestionTypes
from Instructors.views.utils import initialContextDict, current_localtime
from oneUp.decorators import instructorsCheck
from Students.models import StudentRegisteredCourses


def makeContextDictForQuestionsInChallenge(challengeId, context_dict):    # 02/28/15
    
    questionObjects= []
    q_ID = []      #PK for existing answers6
    q_challenge_question_ids = []
    q_preview = []             
    q_type_name = []
    q_type_displayName = []
    q_difficulty = []
    q_position = []
    q_duplicate = []

    # If questionId is specified then we load for editing.
    challenge = Challenges.objects.get(pk=int(challengeId))    
    context_dict['challenge'] = True
    context_dict['challengeID'] = challenge.challengeID
    context_dict['challengeName'] = challenge.challengeName
                      
    # Get the questions for this challenge 
    challenge_questions = ChallengesQuestions.objects.filter(challengeID=int(challengeId)).order_by('questionPosition')
         
    for challenge_question in challenge_questions:
        questionObjects.append(challenge_question.questionID)
        q_position.append(challenge_question.questionPosition)
        q_challenge_question_ids.append(challenge_question.pk)

        if 'unassign' in context_dict:
            problem_filter = ChallengesQuestions.objects.filter(questionID=challenge_question.questionID).exclude(pk=challenge_question.pk)
        else:
            problem_filter = challenge_questions.filter(questionID=challenge_question.questionID).exclude(pk=challenge_question.pk)
        
        affected_problems = [(q.questionID.preview, q.questionPosition, q.challengeID.challengeName) for q in problem_filter]
        q_duplicate.append((len(affected_problems) > 0, affected_problems))
       
 
    for question in questionObjects:
        q_ID.append(question.questionID)
        q_preview.append(question.preview)
        q_type=question.type
        q_type_name.append(QuestionTypes.questionTypes[q_type]['name'])
        q_type_displayName.append(QuestionTypes.questionTypes[q_type]['displayName'])
        q_difficulty.append(question.difficulty)               
        

    # The range part is the index numbers.
    context_dict['question_range'] = list(zip(range(1,len(questionObjects)+1),q_ID,q_challenge_question_ids, q_preview,q_type_name,q_type_displayName, q_difficulty, q_position, q_duplicate))
    return context_dict


def makeContextDictForChallengeList(context_dict, courseId, indGraded):
   
    chall_ID = []      
    chall_Name = []         
    #chall_Category = []
    #chall_Difficulty = []
    chall_visible = []
    chall_available = []
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
            startTime = True
            endTime = True
            #chall_Category.append(item.challengeCategory)
            #chall_Difficulty.append(item.challengeDifficulty)
            if item.isVisible:
                chall_available.append("Available")
            else:
                chall_available.append("Unavailable")
                    
            if item.hasStartTimestamp:
                start_Timestamp.append(item.startTimestamp)

                if item.startTimestamp > current_localtime():
                    startTime = False
            else:
                start_Timestamp.append("")
            
            if item.hasEndTimestamp:
                end_Timestamp.append(item.endTimestamp)
                if item.endTimestamp < current_localtime():
                    endTime = False
            else:
                end_Timestamp.append("")

            if item.hasDueDate:
                chall_due_date.append(item.dueDate)
            else:
                chall_due_date.append("")
            
            if startTime and endTime and item.isVisible:
                
                chall_visible.append("Visible")
            else:
                chall_visible.append("Not Visible")
               
    # The range part is the index numbers.
    context_dict['challenge_range'] = sorted(list(zip(range(1,challenges.count()+1),chall_ID,chall_Name,chall_available,chall_visible,start_Timestamp,end_Timestamp,chall_due_date, chall_Position)), key=lambda tup: tup[8])  ##,chall_Category
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
        #print(context_dict)
    else:
        if not context_dict['ccparams'].seriousChallengesGrouped:
            context_dict = makeContextDictForChallengeList(context_dict, currentCourse, True)
        else:
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
    chall_available = []
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
                    #print("Topics: {}".format(challenge_topics))
                   #print(topic)
                    startTime = True
                    endTime = True
                    item =  challt.challengeID
                    if item.challengeID != UnassignID:
                        chall_ID.append(item.challengeID)
                        chall_Name.append(item.challengeName)
                        chall_position.append(item.challengePosition)

                        if item.isVisible:
                            chall_available.append("Available")
                        else:
                            chall_available.append("Unavailable")
                                
                        if item.hasStartTimestamp:
                            start_Timestamp.append(item.startTimestamp)
                            if item.startTimestamp > current_localtime():
                                startTime = False
                        else:
                            start_Timestamp.append("")
                        
                        if item.hasEndTimestamp:
                            end_Timestamp.append(item.endTimestamp)
                            if item.endTimestamp < current_localtime():
                                endTime = False
                        else:
                            end_Timestamp.append("")

                        if item.hasDueDate:
                            chall_due_date.append(item.dueDate)
                        else:
                            chall_due_date.append("")
                        if startTime and endTime and item.isVisible:
                            chall_visible.append("Visible")
                        else:
                            chall_visible.append("Not Visible")
                    
        return sorted(list(zip(range(1,challenge_topics.count()+1),chall_ID,chall_Name,chall_available, chall_visible, start_Timestamp,end_Timestamp,chall_due_date, chall_position)), key=lambda tup: tup[8])
    else:
        challenge_topics = ChallengesTopics.objects.filter(topicID=topic)
        if challenge_topics:           
            for challt in challenge_topics:
                if Challenges.objects.filter(challengeID=challt.challengeID.challengeID, isGraded=isGraded, courseID=currentCourse):
                    chall_ID.append(challt.challengeID.challengeID)
                    chall_Name.append(challt.challengeID.challengeName)
                    #chall_Difficulty.append(challt.challengeID.challengeDifficulty)
                    chall_position.append(challt.challengeID.challengePosition)
                    startTime = True
                    endTime = True
                    if challt.challengeID.isVisible:
                        chall_available.append('Available')
                    else:
                        chall_available.append('Unavailable')
                    if challt.challengeID.hasStartTimestamp:
                        if challt.challengeID.startTimestamp > current_localtime():
                            startTime = False
                   
                    
                    if challt.challengeID.hasEndTimestamp:
                        if challt.challengeID.endTimestamp < current_localtime():
                            endTime = False

                    if startTime and endTime and challt.challengeID.isVisible:
                        chall_visible.append("Visible")
                    else:
                        chall_visible.append("Not Visible")
                    
        return sorted(list(zip(range(1,challenge_topics.count()+1),chall_ID,chall_Name,chall_available,chall_visible,chall_position)), key=lambda tup: tup[4])

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
        import sys
        topic_ID.append(unspecified_topic.topicID)
        topic_Name.append("Miscellaneous")
        topic_Pos.append(sys.maxsize) 
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
                #print("Registered Event: Challenge Expiration Event, Student: " + str(student.studentID) + ", Challenge: " + str(challenge.challengeID))
