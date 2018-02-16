'''
Created on Sep 5, 2014

@author: Swapna
'''

from django.shortcuts import render
from Instructors.models import Challenges
from Students.models import StudentChallenges, Student
from Students.views.utils import studentInitialContextDict
from datetime import datetime
from django.contrib.auth.decorators import login_required

@login_required
def ChallengesTaken(request):
    
    context_dict,currentCourse = studentInitialContextDict(request)
 
    if 'currentCourseID' in request.session:         
        studentChall_ID = []
        chall_ID = []      
        chall_Name = []         
        chall_Difficulty = []
        dateTaken = []
        score = []
        total = []
        warmUp=0
        
        #Displaying the list of challenges that the student has taken from database
        #studentId = Student.objects.filter(user=request.user)
        studentId = context_dict['student']
        
        if 'warmUp' in request.GET:
            context_dict['warmUp'] = 1
            warmUp=1
                
        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            context_dict['challengeName'] = Challenges.objects.get(pk=request.GET['challengeID']).challengeName
            studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = request.GET['challengeID'])
        else:
            studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse)
            

        if not studentChallenges:
            print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in studentChallenges:
                if (Challenges.objects.filter(challengeID=item.challengeID.challengeID,courseID=currentCourse, isGraded=True)) or (warmUp==1):
                    studentChall_ID.append(item.studentChallengeID) #pk
                    chall_ID.append(item.challengeID.challengeID) 
                    chall_Name.append(item.challengeID.challengeName)
                    chall_Difficulty.append(item.challengeID.challengeDifficulty)
                    strTime = item.startTimestamp
                    dateTaken.append(strTime)
                    score.append(item.testScore)
                    total.append(item.challengeID.totalScore)
                            
                # The range part is the index numbers.
            context_dict['challenge_range'] = zip(range(1,studentChallenges.count()+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)

    return render(request,'Students/ChallengesTaken.html', context_dict)