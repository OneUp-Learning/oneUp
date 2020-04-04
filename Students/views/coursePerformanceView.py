'''
Created on Feb 22, 2017

'''
from django.shortcuts import render
from django.utils import timezone
from Students.models import StudentChallenges, StudentActivities
from Instructors.models import Challenges, Activities
from Instructors.views.utils import localizedDate
from Students.views.utils import studentInitialContextDict
from django.db.models import Q
from Students.views.utils import studentInitialContextDict

from django.contrib.auth.decorators import login_required

@login_required
def CoursePerformance(request):
    # Request the context of the request.
 
    context_dict, currentCourse = studentInitialContextDict(request)            
  
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0
        
        
    student = context_dict['student']          
                
    # Activity and Challenges
    assignmentID = []
    assignmentName = []
    assignmentType = []
    assignmentTime = []
    assignmentGrade = []
    assignmentGradeTotal = []
    assignmentFeedback = []
    isExpired = []

    # Default time is the time that is saved in the database when challenges are created with no dates assigned (AH)
    currentTime = timezone.now()
    
    stud_activities = StudentActivities.objects.filter(studentID=student, courseID=currentCourse).filter(Q(timestamp__lt=currentTime) | Q(hasTimestamp=False))
    for sa in stud_activities:
        assignmentID.append(sa.studentActivityID)
        a = Activities.objects.get(pk=sa.activityID.activityID)
        assignmentName.append(a.activityName)
        assignmentType.append("Activity")
        assignmentTime.append(sa.timestamp)
        assignmentGrade.append(sa.getScoreWithBonus())
        assignmentGradeTotal.append(a.points)
        assignmentFeedback.append(sa.instructorFeedback)
        if currentTime > sa.activityID.endTimestamp:
            isExpired.append(True)
        else:
            isExpired.append(False)

            
    
    # Select if startTime is less than(__lt) currentTime (AH)
    challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(hasStartTimestamp=False))
    
    for challenge in challenges:  
        if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge) :
            
            sChallenges = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge)
            latestSC = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')

            gradeID  = []
                    
            for sc in sChallenges:
                gradeID.append(sc.getScoreWithBonus())

            gMax = (max(gradeID))
            
            assignmentID.append(challenge.challengeID)
            assignmentName.append(challenge.challengeName)
            assignmentType.append("Challenge")
            assignmentTime.append(latestSC.endTimestamp)
            assignmentGrade.append(gMax)
            assignmentGradeTotal.append(latestSC.challengeID.getCombinedScore())
            assignmentFeedback.append("")
            if currentTime > challenge.endTimestamp:
                isExpired.append(True)
            else:
                isExpired.append(False)
    
            
    # The range part is the index numbers.
    context_dict['challenge_range'] = zip(range(1,len(assignmentID)+1),assignmentID,assignmentName,assignmentType, assignmentTime,assignmentGrade, assignmentGradeTotal, assignmentFeedback, isExpired)
    context_dict['challenge_range'] = reversed(sorted(context_dict['challenge_range'], key = lambda t: t[4]))
    
    return render(request,'Students/CoursePerformance.html', context_dict)
