'''
Created on Feb 17, 2018

@author: oumar
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Challenges, Courses
from Students.models import StudentRegisteredCourses, StudentChallenges
from Instructors.views.utils import utcDate, initialContextDict
from Badges.events import register_event
from Badges.enums import Event
from notify.signals import notify
from Badges.event_utils import updateLeaderboard
from oneUp.decorators import instructorsCheck
from decimal import Decimal
import json

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def challengeAdjustmentView(request):
    
    if request.method == 'POST':
        courseId = request.session['currentCourseID']
        course = Courses.objects.get(pk=courseId)
        studentRCs = StudentRegisteredCourses.objects.filter(courseID = courseId)
        challengeId = request.POST['challengeID']
        challenge = Challenges.objects.get(challengeID=challengeId)

        for studentRC in studentRCs:
            studentID = studentRC.studentID.id
            adjustmentScore = Decimal(request.POST['student_AdjustmentScore' + str(studentID)])
            bonusScore = Decimal(request.POST['student_BonusScore' + str(studentID)])
                
            if (StudentChallenges.objects.filter(challengeID=request.POST['challengeID'], studentID=studentID)).exists():
                studentChallenge = StudentChallenges.objects.filter(challengeID=request.POST['challengeID'], studentID=studentID).latest('testScore')
                
                if studentChallenge.scoreAdjustment != adjustmentScore:
                    studentChallenge.scoreAdjustment = adjustmentScore
                    studentChallenge.adjustmentReason = request.POST['adjustmentReason'+str(studentID)]
                    studentChallenge.save()
                    register_event(Event.adjustment,request,studentRC.studentID,challengeId)
                    register_event(Event.leaderboardUpdate,request,studentRC.studentID, challengeId)

                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="Your score for '"+challenge.challengeName+"' was adjusted", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId)}))
                if studentChallenge.bonusPointsAwarded != bonusScore:
                    studentChallenge.bonusPointsAwarded = bonusScore
                    studentChallenge.save()
                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="You've got a bonus for '"+challenge.challengeName+"'", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId)}))
            else:
                if not adjustmentScore == "0" or not bonusScore == "0":
                    studentChallenge = StudentChallenges()
                    studentChallenge.challengeID = challenge
                    studentChallenge.studentID = studentRC.studentID
                    if not adjustmentScore == "0":
                        studentChallenge.scoreAdjustment = adjustmentScore
                        studentChallenge.AdjustmentReason = request.POST['adjustmentReason'+str(studentID)]
                        register_event(Event.adjustment,request,studentRC.studentID,challengeId)
                        register_event(Event.leaderboardUpdate,request,studentRC.studentID, challengeId)
                        notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="Your score for '"+challenge.challengeName+"' was adjusted", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId)}))
                
                    else:
                        studentChallenge.scoreAdjustment = "0"
                        studentChallenge.adjustmentReason = ""

                    if not bonusScore == "0":
                        studentChallenge.bonusPointsAwarded = bonusScore
                        notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="You've got a bonus for '"+challenge.challengeName+"'", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId)}))
                    else:
                        studentChallenge.bonusPointsAwarded = "0"

                    studentChallenge.courseID = course
                    studentChallenge.startTimestamp = utcDate()
                    studentChallenge.endTimestamp = utcDate()
                    studentChallenge.testScore = 0
                    studentChallenge.save()

        updateLeaderboard(course)
        
    return redirect('/oneUp/instructors/challengesList')
    
                
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def adjustmentList(request):
    
    context_dict, currentCourse = initialContextDict(request)
     
    challenge = Challenges.objects.get(challengeID=request.GET['challengeID'])
    context_dict['totalScore'] = challenge.totalScore
           
    student_ID=[]
    student_Name=[]
    student_TestScore=[]
    student_BonusScore=[]
    student_AdjustmentScore=[]
    student_AdjustmentReason=[]
    
    studentRCs = StudentRegisteredCourses.objects.filter(courseID = currentCourse).order_by('studentID__user__last_name')
    
    for studentRC in studentRCs:
        student = studentRC.studentID
        student_ID.append(student.id)
        student_Name.append((student).user.get_full_name())
        
        if (StudentChallenges.objects.filter(challengeID = request.GET['challengeID'], studentID = student)).exists():
            studentChallenge = StudentChallenges.objects.filter(challengeID = request.GET['challengeID'], studentID = student).latest('testScore')
            
            student_TestScore.append(studentChallenge.testScore)
            student_BonusScore.append(studentChallenge.bonusPointsAwarded)
            student_AdjustmentScore.append(studentChallenge.scoreAdjustment)
            student_AdjustmentReason.append(studentChallenge.adjustmentReason)
            
        else:
            student_TestScore.append("-")
            student_BonusScore.append("0")
            student_AdjustmentScore.append("0")
            student_AdjustmentReason.append("")
    
    context_dict['challengeID'] = request.GET['challengeID']
    context_dict['challengeName']= Challenges.objects.get(challengeID=request.GET['challengeID']).challengeName
    context_dict['challengeAdjustment_range'] = zip(range(1,len(student_ID)+1),student_ID,student_Name,student_TestScore, student_BonusScore, student_AdjustmentScore, student_AdjustmentReason) 
            
    return render(request,'Instructors/ChallengeAdjustmentForm.html', context_dict)

            
            
            
            
            
            
            
            
            
            
        
