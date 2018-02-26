'''
Created on Feb 17, 2018

@author: oumar
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Challenges, Courses
from Students.models import StudentRegisteredCourses, StudentChallenges
from Instructors.views.challengeListView import challengesList
from Instructors.views.utils import utcDate
from notify.signals import notify

@login_required
def challengeAdjustmentView(request):
    
    if request.method == 'POST':
        studentRCs = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
        challenge = Challenges.objects.get(challengeID=request.POST['challengeID'])
        
        for studentRC in studentRCs:
            studentID = studentRC.studentID.id
            adjustmentScore = request.POST['student_AdjustmentScore' + str(studentID)]
                
            if (StudentChallenges.objects.filter(challengeID=request.POST['challengeID'], studentID=studentID)).exists():
                studentChallenge = StudentChallenges.objects.filter(challengeID=request.POST['challengeID'], studentID=studentID).latest('testScore')
                
                if not adjustmentScore == "0":
                    studentChallenge.scoreAdjustment = adjustmentScore
                    studentChallenge.adjustmentReason = request.POST['adjustmentReason'+str(studentID)]
                    studentChallenge.save()
                    
                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="You have received an adjustment on the serious challenge '"+challenge.challengeName+"'", nf_type='Challenge Adjustment')

            else:
                if not adjustmentScore == "0":
                    studentChallenge = StudentChallenges()
                    studentChallenge.challengeID = challenge
                    studentChallenge.studentID = studentRC.studentID
                    studentChallenge.scoreAdjustment = adjustmentScore
                    studentChallenge.AdjustmentReason = request.POST['adjustmentReason'+str(studentID)]
                    studentChallenge.courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
                    studentChallenge.startTimestamp = utcDate()
                    studentChallenge.endTimestamp = utcDate()
                    studentChallenge.testScore = 0
                    studentChallenge.save()
                    
                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="You have received an adjustment on the serious challenge '"+challenge.challengeName+"'", nf_type='Challenge Adjustment')

    return redirect('/oneUp/instructors/challengesList')
    
                
@login_required
def adjustmentList(request):
    
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
     
    challenge = Challenges.objects.get(challengeID=request.GET['challengeID'])
    context_dict['totalScore'] = challenge.totalScore
           
    student_ID=[]
    student_Name=[]
    student_TestScore=[]
    student_AdjustmentScore=[]
    student_AdjustmentReason=[]
    
    studentRCs = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID']).order_by('studentID__user__last_name')
    
    for studentRC in studentRCs:
        student = studentRC.studentID
        student_ID.append(student.id)
        student_Name.append((student).user.get_full_name())
        
        if (StudentChallenges.objects.filter(challengeID = request.GET['challengeID'], studentID = student)).exists():
            studentChallenge = StudentChallenges.objects.filter(challengeID = request.GET['challengeID'], studentID = student).latest('testScore')
            
            student_TestScore.append(studentChallenge.testScore)
            student_AdjustmentScore.append(studentChallenge.scoreAdjustment)
            student_AdjustmentReason.append(studentChallenge.adjustmentReason)
            
        else:
            student_TestScore.append("-1")
            student_AdjustmentScore.append("0")
            student_AdjustmentReason.append("")
    
    context_dict['challengeID'] = request.GET['challengeID']
    context_dict['challengeName']= Challenges.objects.get(challengeID=request.GET['challengeID']).challengeName
    context_dict['challengeAdjustment_range'] = zip(range(1,len(student_ID)+1),student_ID,student_Name,student_TestScore, student_AdjustmentScore, student_AdjustmentReason) 
            
    return render(request,'Instructors/ChallengeAdjustmentForm.html', context_dict)

            
            
            
            
            
            
            
            
            
            
        