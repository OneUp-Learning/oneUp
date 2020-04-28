'''
Created on Feb 17, 2018

@author: oumar
'''

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils import timezone
from notify.signals import notify

from Badges.enums import Event
from Badges.event_utils import updateLeaderboard
from Badges.events import register_event
from Badges.models import CourseConfigParams
from Instructors.models import Challenges, Courses
from Instructors.views.utils import current_localtime, initialContextDict, moveTestStudentObjToBottom
from oneUp.decorators import instructorsCheck
from Students.models import StudentChallenges, StudentRegisteredCourses


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def challengeAdjustmentView(request):

    if request.method == 'POST':
        courseId = request.session['currentCourseID']
        course = Courses.objects.get(pk=courseId)
        studentRCs = StudentRegisteredCourses.objects.filter(courseID=courseId)
        challengeId = request.POST['challengeID']
        challenge = Challenges.objects.get(challengeID=challengeId)

        for studentRC in studentRCs:
            studentID = studentRC.studentID.id
            adjustmentScore = Decimal(
                request.POST['student_AdjustmentScore' + str(studentID)])
            if 'student_BonusScore' + str(studentID) in request.POST:
                bonusScore = Decimal(
                    request.POST['student_BonusScore' + str(studentID)])
            else:
                bonusScore = 0

            if (StudentChallenges.objects.filter(challengeID=request.POST['challengeID'], studentID=studentID)).exists():
                studentChallenge = StudentChallenges.objects.filter(
                    challengeID=request.POST['challengeID'], studentID=studentID).latest('testScore')

                if studentChallenge.scoreAdjustment != adjustmentScore:
                    studentChallenge.scoreAdjustment = adjustmentScore
                    studentChallenge.adjustmentReason = request.POST['adjustmentReason'+str(
                        studentID)]
                    studentChallenge.save()
                    register_event(Event.adjustment, request,
                                   studentRC.studentID, challengeId)
                    register_event(Event.leaderboardUpdate, request,
                                   studentRC.studentID, challengeId)

                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="Your score for '"+challenge.challengeName+"' was adjusted", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId), "name": str(course.courseName), "related_link": '/oneUp/students/ChallengesTaken?challengeID='+str(challenge.challengeID)}))
                if studentChallenge.bonusPointsAwarded != bonusScore:
                    studentChallenge.bonusPointsAwarded = bonusScore
                    studentChallenge.save()
                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb="You've got a bonus for '"+challenge.challengeName+"'", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId), "name": str(course.courseName), "related_link": '/oneUp/students/ChallengesTaken?challengeID='+str(challenge.challengeID)}))
            else:

                if not adjustmentScore == 0 or not bonusScore == 0:

                    if not adjustmentScore == 0:
                        studentChallenge = StudentChallenges()
                        studentChallenge.challengeID = challenge
                        studentChallenge.studentID = studentRC.studentID
                        studentChallenge.scoreAdjustment = adjustmentScore
                        studentChallenge.AdjustmentReason = request.POST['adjustmentReason'+str(
                            studentID)]
                        register_event(Event.adjustment, request,
                                       studentRC.studentID, challengeId)
                        register_event(Event.leaderboardUpdate,
                                       request, studentRC.studentID, challengeId)
                        notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                    verb="Your score for '"+challenge.challengeName+"' was adjusted", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId), "name": str(course.courseName), "related_link": '/oneUp/students/ChallengesTaken?challengeID='+str(challenge.challengeID)}))
                        if not bonusScore == 0:
                            studentChallenge.bonusPointsAwarded = bonusScore
                            notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                        verb="You've got a bonus for '"+challenge.challengeName+"'", nf_type='Challenge Adjustment', extra=json.dumps({"course": str(courseId), "name": str(course.courseName), "related_link": '/oneUp/students/ChallengesTaken?challengeID='+str(challenge.challengeID)}))
                        else:
                            studentChallenge.bonusPointsAwarded = 0

                        studentChallenge.courseID = course
                        studentChallenge.startTimestamp = current_localtime()
                        studentChallenge.endTimestamp = current_localtime()
                        studentChallenge.testScore = 0
                        studentChallenge.save()

        updateLeaderboard(course)

    return redirect('/oneUp/instructors/challengesList')


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def adjustmentList(request):

    context_dict, currentCourse = initialContextDict(request)

    challenge = Challenges.objects.get(challengeID=request.GET['challengeID'])
    context_dict['totalScore'] = challenge.totalScore

    student_ID = []
    student_Name = []
    student_TestScore = []
    student_BonusScore = []
    student_AdjustmentScore = []
    student_AdjustmentReason = []

    studentRCs = StudentRegisteredCourses.objects.filter(
        courseID=currentCourse).order_by('studentID__user__last_name')

    for studentRC in studentRCs:
        student = studentRC.studentID
        student_ID.append(student.id)
        if student.isTestStudent:
            student_Name.append("Test Student")
        else:
            student_Name.append((student).user.get_full_name())

        if (StudentChallenges.objects.filter(challengeID=request.GET['challengeID'], studentID=student)).exists():
            studentChallenge = StudentChallenges.objects.filter(
                challengeID=request.GET['challengeID'], studentID=student).latest('testScore')
            if studentChallenge.testScore == 0 and studentChallenge.scoreAdjustment != 0:
                student_TestScore.append("-")
            else:
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
    context_dict['challengeName'] = Challenges.objects.get(
        challengeID=request.GET['challengeID']).challengeName

    student_list = sorted(list(zip(range(1, len(student_ID)+1), student_ID, student_Name,
                                   student_TestScore, student_BonusScore, student_AdjustmentScore, student_AdjustmentReason)))

    student_list = moveTestStudentObjToBottom(student_list)
    #context_dict['challengeAdjustment_range'] = zip(range(1,len(student_ID)+1),student_ID,student_Name,student_TestScore, student_BonusScore, student_AdjustmentScore, student_AdjustmentReason)
    context_dict['challengeAdjustment_range'] = student_list

    isVcUsed = CourseConfigParams.objects.get(courseID=currentCourse).virtualCurrencyUsed
    context_dict['isVcUsed'] = isVcUsed
    return render(request, 'Instructors/ChallengeAdjustmentForm.html', context_dict)
    