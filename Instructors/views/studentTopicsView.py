'''
Created on Oct  2015

@author: Alex
'''
from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import Skills, Courses, CoursesSkills, Topics, CoursesTopics, ChallengesTopics, Challenges
from Students.models import StudentCourseSkills, StudentChallengeQuestions, StudentChallenges, Student
from django.contrib.auth.models import User
from datetime import datetime

from django.contrib.auth.decorators import login_required

@login_required
def studentTopics(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourseId = int(request.session['currentCourseID'])
        currentCourse = Courses.objects.get(pk=currentCourseId)
        context_dict['course_Name'] = currentCourse.courseName
        
        context_dict['page'] = request.GET['page']
        context_dict['userID'] = request.GET['userID']
        user = User.objects.filter(username=request.GET['userID'])
        studentId = Student.objects.filter(user=user)
        

        for u in studentId:
            name = str(u.user.first_name) + ' ' + str(u.user.last_name)
        context_dict['name'] = name
                
        topic_ID = []      
        topic_Name = [] 
        all_challenges = []
        
        course_topics = CoursesTopics.objects.filter(courseID=currentCourseId)
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
                        
                        if StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse,challengeID=chall):
                            item = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse,challengeID=chall)
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
            print(score)
             
        context_dict['topic_range'] = zip(range(1,course_topics.count()+1),topic_ID,topic_Name,all_challenges)

    return render(request,'Instructors/StudentTopics.html', context_dict)