'''
Created on Oct 1, 2015

@author: Alex
'''

from django.shortcuts import render
from Instructors.models import Topics, CoursesTopics, ChallengesTopics, Challenges
from Instructors.constants import  unspecified_topic_name
from Students.models import StudentChallenges
from Students.views.utils import studentInitialContextDict

from django.contrib.auth.decorators import login_required

def challengesForTopic(topic, student, currentCourse):
    challenge_ID = []  
    challenge_Name = [] 
    score = []
    chall_position = []

    challenge_topics = ChallengesTopics.objects.filter(topicID=topic)
    if challenge_topics:           
        for ct in challenge_topics:
            if Challenges.objects.filter(challengeID=ct.challengeID.challengeID, isGraded=False, isVisible=True, courseID=currentCourse):
                challID = ct.challengeID.challengeID
                challenge_ID.append(challID)
                challenge_Name.append(ct.challengeID.challengeName)
                chall_position.append(ct.challengeID.challengePosition)

                if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=challID):
                    item = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=challID)
                    gradeID  = []
                    
                    for sc in item:
                        gradeID.append(sc.testScore)
                    
                    #Calculation for ranking score by 3 levels (Above average, Average, Below Average)
                    tTotal=(sc.challengeID.totalScore/3)
                    
                    #Above Average Score
                    if (max(gradeID) >= (2*tTotal)):
                        score.append(3)
                    #Average Score
                    elif (max(gradeID) > tTotal) and (max(gradeID) < (2*tTotal)):
                        score.append(4)
                    #Below Average Score
                    else:
                        score.append(5)
                else:
                    score.append(2)  # no attempt
    else:
        challenge_ID.append('')
        challenge_Name.append('')
        score.append(1)
        chall_position.append(0)

    #return sorted(list(zip(challenge_Name,challenge_ID,score,chall_position)), key=lambda tup: tup[4])
    return sorted(list(zip(range(1,challenge_topics.count()+1),challenge_Name,challenge_ID,score,chall_position)), key=lambda tup: tup[4])
    
    
@login_required
def ChallengesWarmUpList(request):
    # Request the context of the request.
 
    context_dict,currentCourse = studentInitialContextDict(request)
        
    if 'currentCourseID' in request.session:    
        
        student = context_dict['student']
                
        topic_ID = []      
        topic_Name = [] 
        topic_Pos = []  
        challenges_count = []
        all_challenges_for_topic = []
        
        course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
        hasUnspecifiedTopic = False
        
        for ct in course_topics:
            
            tID = ct.topicID.topicID
            tName = Topics.objects.get(pk=tID).topicName
            if not tName == unspecified_topic_name:   # leave challenges with unspecified topic for last        
                topic_ID.append(tID)
                topic_Name.append(tName)
                topic_Pos.append(str(ct.topicPos))   
                topic_challenges = challengesForTopic(ct.topicID, student, currentCourse) 
                challenges_count.append(len(list(topic_challenges)))
                all_challenges_for_topic.append(topic_challenges)
            else:
                unspecified_topic = ct.topicID  
                hasUnspecifiedTopic = True          

        # Add the challenges with unspecified topic at the end
        if hasUnspecifiedTopic:
            topic_ID.append(unspecified_topic.topicID)
            topic_Name.append("Miscellaneous") 
            topic_Pos.append(str(course_topics.count()))  
            challenges_count.append(len(list(topic_challenges)))
            all_challenges_for_topic.append(challengesForTopic(unspecified_topic, student, currentCourse))

        context_dict['isWarmup'] = True
   
        context_dict['topic_range'] = sorted(list(zip(range(1,course_topics.count()+1),topic_ID,topic_Name,topic_Pos,challenges_count,all_challenges_for_topic)),key=lambda tup: tup[3])
        
    return render(request,'Students/ChallengesWarmUpList.html', context_dict)