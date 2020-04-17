'''
Created on May 27, 2015
Updated 06/09/2017

'''
from audioop import reverse
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Badges.enums import Event
from Badges.events import register_event
from Badges.models import (CourseConfigParams, PeriodicBadges,
                           VirtualCurrencyPeriodicRule)
from Badges.periodicVariables import TimePeriods, studentScore
from Instructors.models import Activities, Challenges, CoursesSkills, Skills
from Students.models import (StudentActivities, StudentBadges,
                             StudentChallenges, StudentConfigParams,
                             StudentCourseSkills, StudentEventLog,
                             StudentRegisteredCourses, StudentStreaks)
from Students.views import classResults
from Students.views.studentCourseHomeView import progress_bar_data
from Students.views.utils import studentInitialContextDict


@login_required
def achievements(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    student = context_dict['student']

    if "is_student" in context_dict:
        if context_dict["is_student"] == True:
            register_event(Event.visitedDashboard, request, student, None)

    st_crs = context_dict['student_registered_course']
    context_dict['course_Bucks'] = str(st_crs.virtualCurrencyAmount)
    context_dict['level'] = str(st_crs.level)

    # PROGRESS BAR
    progress_data = progress_bar_data(
        currentCourse, context_dict['ccparams'], class_scores=False, for_student=student)

    # this is the max points that the student can earn in this course
    progressBarTotalPoints = progress_data['progressBarTotalPoints']

    context_dict['currentEarnedPoints'] = progress_data['currentEarnedPoints']
    context_dict['missedPoints'] = progress_data['missedPoints']
    context_dict['projectedEarnedPoints'] = progress_data['projectedEarnedPoints']
    context_dict['progressBarTotalPoints'] = progress_data['progressBarTotalPoints']
    context_dict['remainingPointsToEarn'] = progress_data['remainingPointsToEarn']

    context_dict['studentXP_range'] = progress_data['xp']

    # Graphs and Tables data
    data = progress_data['data']

    context_dict['challenge_range'] = data['challenge_range']
    context_dict['challengeWithAverage_range'] = data['challengeWithAverage_range']

    context_dict['warmUpContainerHeight'] = data['warmUpContainerHeight']
    context_dict['studentWarmUpChallenges_range'] = data['studentWarmUpChallenges_range']
    context_dict['totalWCEarnedPoints'] = data['totalWCEarnedPoints']
    context_dict['totalWCPossiblePoints'] = data['totalWCPossiblePoints']

    context_dict['skill_range'] = data['skill_range']
    context_dict['nondefskill_range'] = data['nondefskill_range']
    context_dict['skillWithAverage_range'] = data['skillWithAverage_range']

    context_dict["numOfDuelSent"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=872).count()
    context_dict["numOfDuelAccepted"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=873).count()
    context_dict["numOfDuelWon"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=874).count()
    context_dict["numOfDuelLost"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=875).count()
    context_dict["numOfCalloutSent"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=876).count()
    context_dict["numOfCalloutRequest"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=877).count()
    context_dict["numOfCalloutWon"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=878).count()
    context_dict["numOfCalloutLost"] = StudentEventLog.objects.filter(
        student=student, course=currentCourse, event=879).count()

    # Extract Badges data for the current student
    badgeId = []
    badgeName = []
    badgeImage = []
    studentCourseBadges = []

    # Displaying the list of Badges from database
    studentBadges = StudentBadges.objects.filter(
        studentID=student).order_by('timestamp')
    for stud_badge in studentBadges:
        # print('stud_badge.badgeID.courseID'+str(stud_badge.badgeID.courseID))
        if stud_badge.badgeID.courseID == currentCourse:
            studentCourseBadges.append(stud_badge)

    for stud_badge in studentCourseBadges:
        #print('studentBadge: ')
        badgeId.append(stud_badge.badgeID.badgeID)
        #print('studentBadge: '+str(stud_badge))
        badgeName.append(stud_badge.badgeID.badgeName)
        badgeImage.append(stud_badge.badgeID.badgeImage)

    # Query serious challenges table to see if there is any serious challenges
    if Challenges.objects.filter(courseID=currentCourse, isGraded=True):
        context_dict["hasSeriousChallenges"] = True
    else:
        context_dict["hasSeriousChallenges"] = False

    context_dict['badgesInfo'] = list(
        zip(range(1, len(studentCourseBadges)+1), badgeId, badgeName, badgeImage))

    context_dict = displayStreaks(context_dict, student, currentCourse)

    return render(request, 'Students/Achievements.html', context_dict)


def convertTimePeriodToTimePrompt(streakObj):
    daily = 1500  # Runs every day at midnight
    weekly = 1501  # Runs every Sunday at midnight
    biweekly = 1502  # Runs every two weeks on Sunday at midnight
    beginning_of_time = 1503  # Runs only once
    daily_test = 1599

    timePeriod = streakObj.timePeriodID
    print("timeperiod", timePeriod)
    if timePeriod == daily:
        return "Midnight"
    elif timePeriod == weekly:
        return "Sunday at Midnight"
    elif timePeriod == biweekly:
        lastRan = streakObj.lastModified
        nextRun = lastRan + timedelta(days=14)
        return nextRun
    else:
        return "Two Minutes"


def findOutIfStreakChallengeOrAttendance(periodicVariableID):
    if periodicVariableID == 1407:
        return (1, "attendances")
    elif periodicVariableID == 1408 or periodicVariableID == 1409 or periodicVariableID == 1410:
        return (2, "challenges")
    else:
        return (0, "None")


def displayStreaks(context_dict, student, courseID):
    if StudentStreaks.objects.filter(studentID=student, courseID=courseID).exists():
        studentStreaks = StudentStreaks.objects.filter(
            studentID=student, courseID=courseID)
        badgeStreaks = []
        vcStreaks = []

        # find the streaks that are badges and VC
        for studentStreak in studentStreaks:
            # badge
            if studentStreak.streakType == 0:
                badgeStreaks.append(studentStreak)
            # vc
            elif studentStreak.streakType == 1:
                vcStreaks.append(studentStreak)

        badgeStreakName = []
        badgeCurrentStreakLength = []
        badgeTreshhold = []
        badgeType = []
        badgeTime = []
        badgeDescription = []

        print("badgeStreaks", badgeStreaks)
        print("vcStreaks", vcStreaks)
        # find the display information for each streak in each list
        for badgeStreak in badgeStreaks:
            print("badgeStreak", badgeStreak.objectID)
            print("exists", )
            if PeriodicBadges.objects.filter(badgeID=badgeStreak.objectID).exists():
                periodicBadge = PeriodicBadges.objects.get(
                    badgeID=badgeStreak.objectID)
                badgeStreakName.append(periodicBadge.badgeName)
                badgeTreshhold.append(periodicBadge.threshold)
                badgeCurrentStreakLength.append(
                    badgeStreak.currentStudentStreakLength)

                badgeType.append(findOutIfStreakChallengeOrAttendance(
                    periodicBadge.periodicVariableID)[1])
                badgeTime.append(convertTimePeriodToTimePrompt(periodicBadge))
                badgeDescription.append(periodicBadge.badgeDescription)
            print("data", badgeType, badgeStreakName, badgeDescription,
                  badgeCurrentStreakLength, badgeTreshhold, badgeType, badgeTime)
        context_dict['BadgeStreakInfo'] = list(zip(range(1, len(
            badgeType)+1), badgeStreakName, badgeDescription, badgeCurrentStreakLength, badgeTreshhold, badgeType, badgeTime))
        print("context_dict['BadgeStreakInfo']",
              context_dict['BadgeStreakInfo'])

        VCStreakName = []
        VCCurrentStreakLength = []
        vcStreakTreshhold = []
        vcType = []
        vcTime = []
        vcDescription = []
        vcAmount = []

        # find the display information for each streak in each list
        for vcStreak in vcStreaks:
            if VirtualCurrencyPeriodicRule.objects.filter(vcRuleID=vcStreak.objectID).exists():
                vcPeriodicRule = VirtualCurrencyPeriodicRule.objects.get(
                    vcRuleID=vcStreak.objectID)
                VCStreakName.append(vcPeriodicRule.vcRuleName)
                vcStreakTreshhold.append(vcPeriodicRule.threshold)
                VCCurrentStreakLength.append(
                    vcStreak.currentStudentStreakLength)

                vcType.append(findOutIfStreakChallengeOrAttendance(
                    vcPeriodicRule.periodicVariableID)[1])
                vcTime.append(convertTimePeriodToTimePrompt(vcPeriodicRule))
                vcDescription.append(vcPeriodicRule.vcRuleDescription)
                vcAmount.append(vcPeriodicRule.vcRuleAmount)
        context_dict['VCStreakInfo'] = list(zip(range(1, len(
            vcType)+1), VCStreakName, vcDescription, vcAmount, VCCurrentStreakLength, vcStreakTreshhold, vcType, vcTime))
        print("context_dict['VCStreakInfo']", context_dict['VCStreakInfo'])
    return context_dict


@login_required
def Track_class_avg_button_clicks(request):
    # this is used to track how many times the student clicks class average
    # we use ajax to track the information, otherwise they'd get the page refreshed on them
    # and it would be "wrong".
    from django.http import JsonResponse

    context_dictionary, current_course = studentInitialContextDict(request)
    student_id = context_dictionary['student']
    # if we posted data with ajax, use it, otherwise just return.
    if request.POST:
        register_event(Event.clickedViewAverageGrade,
                       request, student_id, None)

        print("ajax call", context_dictionary, student_id)
        return JsonResponse({})

    return render(request, 'Students/Achievements.html', context_dictionary)
