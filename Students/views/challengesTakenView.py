'''
Created on Sep 5, 2014

@author: Swapna
'''

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Instructors.models import Challenges
from Students.models import (Student, StudentChallengeQuestions,
                             StudentChallenges, TeamStudents, Teams, TeamChallenges, TeamChallengeQuestions)
from Students.views.utils import studentInitialContextDict


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
        adjusted_score = []
        has_questions = []
        total = []
        warmUp=0
        
        #Displaying the list of challenges that the student has taken from database
        #studentId = Student.objects.filter(user=request.user)
        studentId = context_dict['student']
        
        if 'warmUp' in request.GET:
            context_dict['warmUp'] = 1
            warmUp=1
        if 'all' in request.GET:
            context_dict['all'] = True
        if 'classAchievements' in request.GET:
            context_dict['classAchievements'] = True
               
        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            context_dict['challengeName'] = Challenges.objects.get(pk=request.GET['challengeID']).challengeName
            studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = request.GET['challengeID'])
        else:
            studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse)
            
        if 'isExpired' in request.GET:
            if str(request.GET['isExpired']) == 'True':
                context_dict['isExpired'] = True
            else:
                context_dict['isExpired'] = False
        if 'teams' in request.GET:
            context_dict['teams'] = True
            teamChallengesTaken(context_dict, currentCourse)
        else:

            if not studentChallenges:
                print('No challenge')
                context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
            else:
                for item in studentChallenges:
                    if Challenges.objects.filter(challengeID=item.challengeID.challengeID,courseID=currentCourse, isGraded=True) or warmUp==1:
                        studentChall_ID.append(item.studentChallengeID) #pk
                        chall_ID.append(item.challengeID.challengeID) 
                        chall_Name.append(item.challengeID.challengeName)
                        chall_Difficulty.append(item.challengeID.challengeDifficulty)
                        endTime = item.endTimestamp
                        dateTaken.append(endTime)
                        score.append(item.testScore)
                        adjusted_score.append(item.getScoreWithBonus())
                        has_questions.append(StudentChallengeQuestions.objects.filter(studentChallengeID=item).exists())
                        total.append(item.challengeID.totalScore)
                                
                    # The range part is the index numbers.
                context_dict['challenge_range'] = sorted(list(zip(range(1,studentChallenges.count()+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score, adjusted_score, total, has_questions)), key=lambda item: item[5], reverse=True)

    return render(request,'Students/ChallengesTaken.html', context_dict)

def teamChallengesTaken(context_dict, course):
    team_names = []
    team_challenges = []
    studentChall_ID = []
    chall_ID = []      
    chall_Name = []         
    dateTaken = []
    score = []
    adjusted_score = []
    has_questions = []
    total = []

    studentID = context_dict['student']
    student_attempts = TeamChallenges.objects.filter(challengeID=context_dict['challengeID'], courseID=course)
    for attempt in student_attempts:
        student_teams = TeamStudents.objects.filter(studentID=studentID, teamID=attempt.teamID).first()
        if student_teams:
            item = {
                'teamName': attempt.teamID.teamName,
                'challengeName': attempt.challengeID.challengeName,
                'dateTaken':attempt.endTimestamp,
                'score':attempt.testScore,
                'adjustment':attempt.scoreAdjustment,
                'max':attempt.challengeID.totalScore,
                'hasQuestions':TeamChallengeQuestions.objects.filter(teamChallengeID=attempt).exists(),
                'challengeID': attempt.challengeID.challengeID,
                'teamChallengeID': attempt.teamChallengeID,
                'teamID':attempt.teamID.teamID
            }
            team_challenges.append(item)
            
    context_dict['team_challenges'] = sorted(team_challenges, key=lambda item:item.get('dateTaken'), reverse=True)






