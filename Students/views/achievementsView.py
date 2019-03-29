'''
Created on May 27, 2015
Updated 06/09/2017

'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.models import Skills, Challenges, CoursesSkills, Activities, Milestones
from Students.models import StudentCourseSkills, StudentChallenges, StudentBadges, StudentRegisteredCourses, StudentActivities
from Badges.models import CourseConfigParams
from Students.views import classResults
from Students.views.utils import studentInitialContextDict
from Students.models import StudentConfigParams

from Badges.periodicVariables import studentScore, TimePeriods
from Badges.events import register_event
from Badges.enums import Event
from audioop import reverse


@login_required
def achievements(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    context_dict["logged_in"] = request.user.is_authenticated

    studentId = context_dict['student']

    if "is_student" in context_dict:
        if context_dict["is_student"] == True:
            register_event(Event.visitedDashboard, request, studentId, None)

    st_crs = StudentRegisteredCourses.objects.get(
        studentID=studentId, courseID=currentCourse)
    context_dict['avatar'] = st_crs.avatarImage
    context_dict['course_Bucks'] = str(st_crs.virtualCurrencyAmount)

    curentStudentConfigParams = StudentConfigParams.objects.get(
        courseID=currentCourse, studentID=studentId)
    context_dict['is_ClassAverage_Displayed'] = str(
        curentStudentConfigParams.displayClassAverage)
    context_dict['are_Badges_Displayed'] = str(
        curentStudentConfigParams.displayBadges)

    time_period = TimePeriods.timePeriods[1503]
    context_dict, xp, totalScorePointsSeriousChallenge, totalScorePointsWarmupChallenge, earnedActivityPoints, totalScorePointsSkillPointsWeighted, totalScorePointsActivityPoints, totalPointsSeriousChallenges = studentScore(
        studentId, currentCourse, 0, time_period, 0, result_only=True, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, context_dict=context_dict)
    context_dict['studentXP_range'] = xp

    # print("xp", xp, earnedPointsSeriousChallengesWeighted, totalScorePointsWCWeighted,
    #      totalScorePointsSPWeighted, earnedActivityPointsWeighted)

    context_dict['studentUngradedChallengesPPoints_range'] = totalScorePointsSkillPointsWeighted
    # End Vendhan Changes

 # PROGRESS BAR

    # MILESTONES
    # this is the max points that the student can earn in this course
    totalMilestonePoints = 0
    milestones = Milestones.objects.filter(courseID=currentCourse)
    for stone in milestones:
        totalMilestonePoints += stone.points

    currentEarnedPoints = totalScorePointsSeriousChallenge + earnedActivityPoints
    currentTotalPoints = totalPointsSeriousChallenges + totalScorePointsActivityPoints
    missedPoints = currentTotalPoints - currentEarnedPoints
    if not currentTotalPoints == 0:
        projectedEarnedPoints = round(
            currentEarnedPoints * totalMilestonePoints/currentTotalPoints)
    else:
        projectedEarnedPoints = 0
    remainingPointsToEarn = totalMilestonePoints - currentTotalPoints

    print("totalMilestonePoints", totalMilestonePoints)
    print("currentEarnedPoints", currentEarnedPoints)
    print("currentTotalPoints", currentTotalPoints)
    print("missedPoints", missedPoints)
    print("projectedEarnedPoints", projectedEarnedPoints)
    print("remainingPointsToEarn", remainingPointsToEarn)

    context_dict['currentEarnedPoints'] = currentEarnedPoints
    context_dict['missedPoints'] = missedPoints
    context_dict['projectedEarnedPoints'] = projectedEarnedPoints
    context_dict['totalMilestonePoints'] = totalMilestonePoints
    context_dict['remainingPointsToEarn'] = remainingPointsToEarn

    # Extract Badges data for the current student
    badgeId = []
    badgeName = []
    badgeImage = []
    studentCourseBadges = []

    # Displaying the list of Badges from database
    studentBadges = StudentBadges.objects.filter(
        studentID=studentId).order_by('timestamp')
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

        # The range part is the index numbers.
    #context_dict['badgesInfo'] = zip(range(1,studentBadges.count()+1),badgeId,badgeName,badgeImage)
    context_dict['badgesInfo'] = list(
        zip(range(1, len(studentCourseBadges)+1), badgeId, badgeName, badgeImage))

    return render(request, 'Students/Achievements.html', context_dict)
