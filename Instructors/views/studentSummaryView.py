'''
Created on Feb 12, 2018

@author: hodgeaustin
'''

from django.template import RequestContext
from django.shortcuts import render

from oneUp.auth import createStudents, checkPermBeforeView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Instructors.models import Courses, Challenges, Activities, CoursesSkills, Skills
from Instructors.views.utils import initialContextDict, utcDate
from Instructors.constants import default_time_str
from Instructors.views.instructorCourseHomeView import studentXP
from Students.models import Student, StudentRegisteredCourses, StudentChallenges, StudentActivities, StudentCourseSkills, StudentEventLog
from Badges.enums import Event
    
@login_required
def studentSummary(request):
    
    context_dict, currentCourse = initialContextDict(request)
    
    userID = []
    first_Name = []
    last_Name = []
    user_Avatar = []
    user_Action = []
    # Serious Challenge (sc)
    sc_totalStudentScore = []
    sc_totalStudentPossibleScore = []
    # Activities (act)
    act_totalStudentScore = []
    act_totalStudentPossibleScore = []
    # Warmup Challenge (wc)
    wc_totalStudentUniqueTaken = []
    wc_totalStudentAttempts = []
    
    user_XP = []
    user_VC = []

    courseStudents = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    courseChallenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True)
    defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
    # default time
    courseActivities = Activities.objects.filter(courseID=currentCourse, endTimestamp__lt=defaultTime)
    courseWarmupChallenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False, isVisible=True)
    
    studentEvents = [Event.startChallenge, Event.endChallenge, Event.userLogin, Event.studentUpload, Event.spendingVirtualCurrency,
                     Event.visitedDashboard, Event.visitedEarnedVCpage, Event.visitedBadgesInfoPage, Event.visitedSpendedVCpage,
                     Event.visitedVCRulesInfoPage]
    
    for cs in courseStudents:
        s = cs.studentID
        userID.append(s.user)
        first_Name.append(s.user.first_name)
        last_Name.append(s.user.last_name)
        user_Avatar.append(cs.avatarImage)
        
        last_action = StudentEventLog.objects.filter(course=currentCourse, student = s, event__in = studentEvents).order_by('-timestamp').first()
        if last_action:
            user_Action.append(last_action.timestamp)
        else:
            user_Action.append("None")
        
        # Getting Serious Challenge total points earned by student and total possible points earned
        sc_totalPointsReceived = 0
        sc_totalPointsPossible = 0
        
        for seriousChallenge in courseChallenges:
            studentChallenges = StudentChallenges.objects.filter(courseID=currentCourse, studentID = s, challengeID = seriousChallenge)
            sc_totalPointsPossible += seriousChallenge.totalScore
            if studentChallenges.exists():
                scores = [sc.testScore for sc in studentChallenges]
                sc_totalPointsReceived += max(scores)
                            
        sc_totalStudentScore.append(sc_totalPointsReceived)
        sc_totalStudentPossibleScore.append(sc_totalPointsPossible)
        
        
        # Getting Activity total points earned by student and total points earned
        act_totalPointsRecieved = 0
        act_totalPointsPossible = 0
        
        for activity in courseActivities:
            studentActivities = StudentActivities.objects.filter(studentID=s, courseID=currentCourse,activityID=activity)
            act_totalPointsPossible += activity.points
            if studentActivities.exists():     
                scores = [sa.activityScore for sa in studentActivities]
                act_totalPointsRecieved += max(scores) 
                        
        act_totalStudentScore.append(act_totalPointsRecieved)
        act_totalStudentPossibleScore.append(act_totalPointsPossible)
        
        
        # Getting Warmup Challenge total unique taken by student and attempts
        wc_totalUniqueTaken = 0
        wc_totalAttempts = 0
        
        for warmupChallenge in courseWarmupChallenges:
            studentChallenges = StudentChallenges.objects.filter(courseID=currentCourse, studentID = s, challengeID = warmupChallenge)
            wc_totalAttempts += studentChallenges.count()
            if studentChallenges.exists():
                wc_totalUniqueTaken += 1
               
        wc_totalStudentUniqueTaken.append(wc_totalUniqueTaken)
        wc_totalStudentAttempts.append(wc_totalAttempts)
        

        user_XP.append(studentXP(s, currentCourse))
        user_VC.append(cs.virtualCurrencyAmount)
        
    # The range part is the index numbers.
    context_dict['user_range'] = sorted(list(zip(range(1,courseStudents.count()+1),userID,first_Name,last_Name,user_Avatar, sc_totalStudentScore, 
                                     sc_totalStudentPossibleScore, act_totalStudentScore, act_totalStudentPossibleScore,
                                     wc_totalStudentUniqueTaken, wc_totalStudentAttempts, user_XP, user_VC, user_Action)), key=lambda tup: tup[3])

    return render(request,'Instructors/StudentSummary.html', context_dict)