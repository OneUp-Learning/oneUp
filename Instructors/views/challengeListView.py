'''
Created on Apr 7, 2014

@author: dichevad
'''
from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import Courses, Challenges, ChallengesQuestions

from django.contrib.auth.decorators import login_required
from Instructors.models import Challenges
from Badges.events import register_event
from Badges.enums import Event, QuestionTypes
from time import strftime
from Students.models import StudentChallenges, StudentRegisteredCourses
from _datetime import datetime, tzinfo
from time import time, strptime, struct_time
from time import strftime
import datetime

from Instructors.constants import unassigned_problems_challenge_name


def makeContextDictForQuestionsInChallenge(challengeId, context_dict):    # 02/28/15
    
    questionObjects= []
    qlist = []
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
            if item.isVisible == False:
                chall_visible.append("*Not Visible*")
            else:
                chall_visible.append("Visible")
                    
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
def ChallengesList(request):
    
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
            