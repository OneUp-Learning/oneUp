'''
Created on Feb 12, 2018

@author: hodgeaustin
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from Badges.enums import Event
from Badges.models import CourseConfigParams
from Badges.periodicVariables import studentScore
from Instructors.models import Activities, Challenges
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Students.models import (StudentActivities, StudentChallenges,
                             StudentEventLog, StudentRegisteredCourses,studentFlashCards)
from Students.views.avatarView import checkIfAvatarExist


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
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
    user_flashCards = []
    context_dict['isVCUsed'] = CourseConfigParams.objects.get(courseID=currentCourse).virtualCurrencyUsed
    context_dict['warmupsUsed'] = CourseConfigParams.objects.get(courseID=currentCourse).warmupsUsed
    context_dict['seriousUsed'] = CourseConfigParams.objects.get(courseID=currentCourse).seriousChallengesUsed
    context_dict['activitiesUsed'] = CourseConfigParams.objects.get(courseID=currentCourse).activitiesUsed
    context_dict['flashcardsUsed'] = CourseConfigParams.objects.get(courseID=currentCourse).flashcardsUsed
    
    courseStudents = StudentRegisteredCourses.objects.filter(
        courseID=currentCourse).exclude(studentID__isTestStudent=True)
    courseChallenges = Challenges.objects.filter(
        courseID=currentCourse, isGraded=True, isVisible=True)
    courseActivities = Activities.objects.filter(courseID=currentCourse)
    courseWarmupChallenges = Challenges.objects.filter(
        courseID=currentCourse, isGraded=False)

    studentEvents = [Event.startChallenge, Event.endChallenge, Event.userLogin, Event.studentUpload, Event.spendingVirtualCurrency,
                     Event.visitedDashboard, Event.visitedEarnedVCpage, Event.visitedBadgesInfoPage, Event.visitedSpendedVCpage,
                     Event.visitedVCRulesInfoPage, Event.submitFlashCard, Event.viewFlashCard]

    for cs in courseStudents:
        s = cs.studentID
        userID.append(s.user)
        first_Name.append(s.user.first_name)
        last_Name.append(s.user.last_name)
        user_Avatar.append(checkIfAvatarExist(cs))

        last_action = StudentEventLog.objects.filter(
            course=currentCourse, student=s, event__in=studentEvents).order_by('-timestamp').first()
        if last_action:
            user_Action.append(last_action.timestamp)
        else:
            user_Action.append("None")

        # Getting Serious Challenge total points earned by student and total possible points earned
        sc_totalPointsReceived = 0
        sc_totalPointsPossible = 0

        for seriousChallenge in courseChallenges:
            studentChallenges = StudentChallenges.objects.filter(
                courseID=currentCourse, studentID=s, challengeID=seriousChallenge)
            sc_totalPointsPossible += seriousChallenge.getCombinedScore()
            if studentChallenges.exists():
                scores = [sc.getScore() for sc in studentChallenges]
                sc_totalPointsReceived += max(scores)

        sc_totalStudentScore.append(sc_totalPointsReceived)
        sc_totalStudentPossibleScore.append(sc_totalPointsPossible)

        # Getting Activity total points earned by student and total points earned
        act_totalPointsRecieved = 0
        act_totalPointsPossible = 0

        for activity in courseActivities:
            studentActivities = StudentActivities.objects.filter(
                studentID=s, courseID=currentCourse, activityID=activity)
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
            studentChallenges = StudentChallenges.objects.filter(
                courseID=currentCourse, studentID=s, challengeID=warmupChallenge)
            wc_totalAttempts += studentChallenges.count()
            if studentChallenges.exists():
                wc_totalUniqueTaken += 1

        wc_totalStudentUniqueTaken.append(wc_totalUniqueTaken)
        wc_totalStudentAttempts.append(wc_totalAttempts)

        result = studentScore(s, currentCourse, 0, result_only=True)
        xp = result['xp']
        user_XP.append(xp)
        user_VC.append(cs.virtualCurrencyAmount)
        
        user_flashCards.append( studentFlashCards.objects.filter( studentID =s ).count())

    # The range part is the index numbers.
    context_dict['user_range'] = sorted(list(zip(range(1, courseStudents.count()+1), userID, first_Name, last_Name, user_Avatar, sc_totalStudentScore,
                                                 sc_totalStudentPossibleScore, act_totalStudentScore, act_totalStudentPossibleScore,
                                                 wc_totalStudentUniqueTaken, wc_totalStudentAttempts, user_XP, user_VC, user_flashCards, user_Action)), key=lambda tup: tup[3])

    return render(request, 'Instructors/StudentSummary.html', context_dict)
