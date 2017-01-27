'''
Created on August 2015

@author: Alex
'''

from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Courses, Challenges
from Students.models import StudentChallenges, Student
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def studentChallengesCompleted(request):
    
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        studentChall_ID = []
        chall_ID = []      
        chall_Name = []         
        chall_Difficulty = []
        dateTaken = []
        score = []
        total = []
        first_Name = []      
        last_Name = []
        chall_N = []
        
        if request.GET['userID'] == '-':
            context_dict['no_challenge'] = 'No challenge have being taken'
        else:
            
            user = User.objects.filter(username=request.GET['userID'])
            studentId = Student.objects.filter(user=user)
            context_dict['userID'] = request.GET['userID']
            
            if 'page' in request.GET:
                context_dict['page'] = request.GET['page']
                if request.GET['page'] == "3":
                    graded = True
                else:
                    graded = False
            else:
                graded = True
 
            for u in studentId:
                first_Name.append(u.user.first_name)
                last_Name.append(u.user.last_name)

            if 'challengeID' in request.GET:
                challengeID = request.GET['challengeID']
                context_dict['challengeID'] = challengeID
                print(studentId)
                studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID=challengeID)
                print(studentChallenges)
            else: 
                studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse)
            
            for item in studentChallenges: 
                if Challenges.objects.filter(challengeID=item.challengeID.challengeID, courseID=currentCourse, isGraded=graded):
                    studentChall_ID.append(item.studentChallengeID) 
                    chall_ID.append(item.challengeID.challengeID) 
                    chall_Name.append(item.challengeID.challengeName)
                    chall_Difficulty.append(item.challengeID.challengeDifficulty)
                    strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                    dateTaken.append(strTime)
                    score.append(item.testScore)
                    total.append(item.testTotal)
                                
                context_dict['challenge_range'] = zip(range(1,studentChallenges.count()+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)
                context_dict['user_name'] = zip(first_Name,last_Name)

    return render(request,'Instructors/StudentChallengesCompleted.html', context_dict)