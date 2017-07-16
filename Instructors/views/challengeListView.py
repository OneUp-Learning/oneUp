'''
Created on Apr 7, 2014
Last updated 07/15/2017

@author: dichevad
'''
from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import Courses, Challenges, ChallengesQuestions, Topics, CoursesTopics, ChallengesTopics
from Instructors.constants import  unspecified_topic_name
from django.contrib.auth.decorators import login_required
from Badges.events import register_event
from Badges.enums import Event, QuestionTypes
from Students.models import StudentRegisteredCourses
#from _datetime import datetime, tzinfo
from time import time, strptime, struct_time
from time import strftime
import datetime

from Instructors.constants import unassigned_problems_challenge_name


def makeContextDictForQuestionsInChallenge(challengeId, context_dict):    # 02/28/15
    
    questionObjects= []
    q_ID = []      #PK for existing answers6
    q_preview = []             
    q_type_name = []
    q_type_displayName = []
    q_difficulty = []

    # If questionId is specified then we load for editing.
    challenge = Challenges.objects.get(pk=int(challengeId))    
    context_dict['challenge'] = True
    context_dict['challengeID'] = challenge.challengeID
    context_dict['challengeName'] = challenge.challengeName
                      
    # Get the questions for this challenge 
    challenge_questions = ChallengesQuestions.objects.filter(challengeID=int(challengeId))
         
    for challenge_question in challenge_questions:
        questionObjects.append(challenge_question.questionID)
 
    for question in questionObjects:
        q_ID.append(question.questionID)
        q_preview.append(question.preview)
        q_type=question.type
        q_type_name.append(QuestionTypes.questionTypes[q_type]['name'])
        q_type_displayName.append(QuestionTypes.questionTypes[q_type]['displayName'])
        q_difficulty.append(question.difficulty)
                
        
    # The range part is the index numbers.
    context_dict['question_range'] = zip(range(1,len(questionObjects)+1),q_ID,q_preview,q_type_name,q_type_displayName, q_difficulty)   
    
    return context_dict


def makeContextDictForChallengeList(context_dict, courseId, indGraded):
   
    chall_ID = []      
    chall_Name = []         
    #chall_Category = []
    chall_Difficulty = []
    chall_visible = []
    start_Timestamp = []
    end_Timestamp = []
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
            #chall_Category.append(item.challengeCategory)
            chall_Difficulty.append(item.challengeDifficulty)
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
               
    # The range part is the index numbers.
    context_dict['challenge_range'] = zip(range(1,challenges.count()+1),chall_ID,chall_Name,chall_Difficulty,chall_visible,start_Timestamp,end_Timestamp)  ##,chall_Category
    return context_dict


@login_required
def challengesList(request):
    
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    if 'warmUp' in request.GET:
            warmUp = 1
            context_dict['warmUp']= 1
    else:
        warmUp = 0    

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        # True -> the challenge is graded
        if warmUp == 1:
            context_dict = makeContextDictForChallengeList(context_dict, currentCourse, False)
        else:
            context_dict = makeContextDictForChallengeList(context_dict, currentCourse, True)
    else:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
        
    disableExpiredChallenges(request)

    return render(request,'Instructors/ChallengesList.html', context_dict)
    

def challengesForTopic(topic):

    chall_ID = []  
    chall_Name = [] 
    chall_Difficulty = []
    chall_visible = []
    
    challenge_topics = ChallengesTopics.objects.filter(topicID=topic)
    if challenge_topics:           
        for challt in challenge_topics:
            if Challenges.objects.filter(challengeID=challt.challengeID.challengeID, isGraded=False, isVisible=True):
                chall_ID.append(challt.challengeID.challengeID)
                chall_Name.append(challt.challengeID.challengeName)
                chall_Difficulty.append(challt.challengeID.challengeDifficulty)
                if challt.challengeID.isVisible:
                    chall_visible.append('Visible')
                else:
                    chall_visible.append('Not Visible')

    #return zip(challenge_Name,challenge_ID, challenge_Difficulty, isVisible)
    return zip(range(1,challenge_topics.count()+1),chall_ID,chall_Name,chall_Difficulty,chall_visible)

def warmUpChallengeList(request):
    
    # Warm challenged will be grouped by course topics
    
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'      
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName

        topic_ID = []      
        topic_Name = [] 
        all_challenges_for_topic = []

        course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
        for ct in course_topics:
            
            tID = ct.topicID.topicID
            tName = Topics.objects.get(pk=tID).topicName
            if not tName == unspecified_topic_name:   # leave challenges with unspecified topic for last        
                topic_ID.append(tID)
                topic_Name.append(tName)
            
            all_challenges_for_topic.append(challengesForTopic(ct.topicID))
        
        # Add the challenges with unspecified topic at the end
        unsp_topic = Topics.objects.filter(topicName=unspecified_topic_name)
        if unsp_topic:
            unsp_topicID = unsp_topic[0].topicID
            topic_ID.append(unsp_topicID)
            topic_Name.append(" ")   
            all_challenges_for_topic.append(challengesForTopic(unsp_topicID))
                         
        context_dict['topic_range'] = zip(range(1,course_topics.count()+1),topic_ID,topic_Name,all_challenges_for_topic)

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
            