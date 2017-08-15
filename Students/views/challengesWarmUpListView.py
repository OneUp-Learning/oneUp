'''
Created on Oct 1, 2015

@author: Alex
'''

from django.shortcuts import render
from Instructors.models import Topics, CoursesTopics, ChallengesTopics, Challenges
from Students.models import StudentChallenges
from Students.views.utils import studentInitialContextDict


from django.contrib.auth.decorators import login_required

@login_required
def ChallengesWarmUpList(request):
    # Request the context of the request.
 
    context_dict,currentCourse = studentInitialContextDict(request)
        
    if 'currentCourseID' in request.session:    
        
        student = context_dict['student']
                
        topic_ID = []      
        topic_Name = [] 
        all_challenges = []
        
        course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
        for t in course_topics:
            
            tID = t.topicID.topicID
            tName = Topics.objects.get(pk=tID).topicName
            topic_ID.append(tID)
            topic_Name.append(tName)
            
            challenge_ID = []  
            challenge_Name = [] 
            score = []

            challenge_topic = ChallengesTopics.objects.filter(topicID=tID)
            if challenge_topic:           
                for ct in challenge_topic:
                    if Challenges.objects.filter(challengeID=ct.challengeID.challengeID, isGraded=False, isVisible=True):
                        chall = ct.challengeID.challengeID
                        challenge_ID.append(chall)
                        challenge_Name.append(ct.challengeID.challengeName)
    
                        if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=chall):
                            item = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=chall)
                            gradeID  = []
                            
                            for sc in item:
                                gradeID.append(sc.testScore)
                            
                            #Calculation for ranking score by 3 levels (Above average, Average, Below Average)
                            tTotal=(sc.testTotal/3)
                            
                            #Above Average Score
                            if (max(gradeID) >= (2*tTotal)) or (max(gradeID) == (3*tTotal)):
                                score.append(3)
                            #Average Score
                            elif (max(gradeID) > tTotal) or (max(gradeID) <= (2*tTotal)):
                                score.append(4)
                            #Below Average Score
                            else:
                                score.append(5)
                        else:
                            score.append(2)
            else:
                challenge_ID.append('')
                challenge_Name.append('')
                score.append(1)

            all_challenges.append(zip(challenge_Name,challenge_ID,score))
             
        context_dict['topic_range'] = zip(range(1,course_topics.count()+1),topic_ID,topic_Name,all_challenges)

    return render(request,'Students/ChallengesWarmUpList.html', context_dict)