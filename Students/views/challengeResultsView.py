'''
Created on Jun 12, 2014
Updated May/10/2017

@author: iiscs
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from Instructors.views.utils import utcDate
from Instructors.models import Questions, CorrectAnswers, Challenges, Courses, QuestionsSkills, Answers, MatchingAnswers, DynamicQuestions, StaticQuestions,\
    ChallengesQuestions
from Students.models import StudentCourseSkills, Student, StudentChallenges, StudentChallengeQuestions, StudentChallengeAnswers, DuelChallenges, CalloutParticipants, CalloutStats
from Students.views.utils import studentInitialContextDict
from Students.views.duelChallengeView import duel_challenge_evaluate
from Students.views.calloutsView import evaluator
from Badges.events import register_event
from Badges.event_utils import updateLeaderboard
from Badges.enums import Event
from Instructors.questionTypes import QuestionTypes, dynamicQuestionTypesSet, staticQuestionTypesSet, questionTypeFunctions
from Instructors.lupaQuestion import LupaQuestion, lupa_available, CodeSegment
from Instructors.views.dynamicQuestionView import makeLibs
from Badges.systemVariables import logger
from Students.views.challengeSetupView import makeSerializableCopyOfDjangoObjectDictionary
import re
import math
import pytz
from decimal import Decimal
from oneUp.ckeditorUtil import config_ck_editor
from Students.views.challengeSetupView import remove_old_challenge_session_entries


def saveSkillPoints(questionId, course, studentId, studentChallengeQuestion):

    # get all skills to which this question contributes
    questionSkills = QuestionsSkills.objects.filter(
        questionID=questionId, courseID=course)
    if questionSkills:
        for qskill in questionSkills:

            # check if this question has already been answered and contributed to the skill
            # qss is all appearances of this question in StudentCourseSkills
            qss = StudentCourseSkills.objects.filter(studentChallengeQuestionID__questionID__questionID=questionId,
                                                     studentChallengeQuestionID__studentChallengeID__studentID=studentId, skillID=qskill.skillID)

            if not qss:
                studentCourseSkills = StudentCourseSkills()
                studentCourseSkills.studentChallengeQuestionID = studentChallengeQuestion
                studentCourseSkills.skillID = qskill.skillID
                studentCourseSkills.skillPoints = qskill.questionSkillPoints
                studentCourseSkills.save()

    return


def saveChallengeQuestion(studentChallenge, key, ma_point, c_ques_points, instructorFeedback, seed):

    studentChallengeQuestion = StudentChallengeQuestions()
    studentChallengeQuestion.studentChallengeID = studentChallenge
    studentChallengeQuestion.questionID = Questions(key)
    studentChallengeQuestion.questionScore = ma_point
    studentChallengeQuestion.questionTotal = c_ques_points
    studentChallengeQuestion.usedHint = "False"
    #studentChallengeQuestion.instructorFeedback = instructorFeedback
    studentChallengeQuestion.seed = seed
    studentChallengeQuestion.save()
    return studentChallengeQuestion


@login_required
def ChallengeResults(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    if 'currentCourseID' in request.session:
         # Intially by default its saved none.. Updated after instructor's evaluation

        # This is included so that we can avoid magic numbers for question types in the template.
        context_dict['questionTypes'] = QuestionTypes

        if request.POST:

            studentId = Student.objects.get(user=request.user)

            if request.POST['challengeId'] == "":
                # Challenge without questions
                print('here')
                print(request.POST['challengeId'])
                if 'duelID' in request.POST:
                    duel_id = request.POST['duelID']
                    return redirect('/oneUp/students/DuelChallengeDescription?duelChallengeID='+duel_id)
                elif 'calloutPartID' in request.POST:
                    call_out_part_id = request.POST['calloutPartID']
                    return redirect("/oneUp/students/CalloutDescription?call_out_participant_id="+call_out_part_id+"&participant_id="+studentId.user.id)

                return redirect('/oneUp/students/ChallengesList')

            else:
                #print (studentId)

                challengeId = request.POST['challengeId']
                course = Courses.objects.get(pk=currentCourse.courseID)
                challenge = Challenges.objects.get(pk=challengeId)
                is_duel = False
                is_call_out = False
                context_dict['challengeName'] = challenge.challengeName
                context_dict['showcorrect'] = challenge.displayCorrectAnswer
                if 'duelID' in request.POST:
                    duel_id = request.POST['duelID']
                    is_duel = True
                    duel_challenge = DuelChallenges.objects.get(
                        pk=int(duel_id))
                    context_dict['duelID'] = duel_id
                    context_dict['isDuel'] = True
                    context_dict['challengeName'] = duel_challenge.duelChallengeName
                elif "calloutPartID" in request.POST:
                    call_out_part_id = request.POST['calloutPartID']
                    context_dict['participantID'] = studentId.user.id
                    is_call_out = True
                    call_out_part = CalloutParticipants.objects.get(
                        pk=int(call_out_part_id))
                    context_dict['isCallout'] = is_call_out
                    context_dict['calloutPartID'] = call_out_part_id
                    context_dict['challengeName'] = call_out_part.calloutID.challengeID.challengeName

                #context_dict['instructorFeedback'] = challenge.instructorFeedback

                if not challenge.isGraded:
                    print("warmUp")
                    context_dict['warmUp'] = 1

                print("Start Time: "+request.POST['startTime'])
                startTime = utcDate(
                    request.POST['startTime'], "%m/%d/%Y %I:%M:%S %p").replace(tzinfo=None).astimezone(pytz.utc)
                # end time of the test is the current time when it is navigated to this page
                endTime = utcDate()
                print("End Time:" + endTime.strftime("%m/%d/%Y %I:%M %p"))

                attemptId = 'challenge:'+challengeId + \
                    '@' + request.POST['startTime']
                print("attemptID = "+attemptId)

                # Do not grade the same challenge twice
                if StudentChallenges.objects.filter(challengeID=challengeId, studentID=studentId, startTimestamp=startTime).count() > 0:
                    return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)

                # save initial student-challenge information pair (no score)to db
                studentChallenge = StudentChallenges()
                studentChallenge.studentID = studentId
                studentChallenge.courseID = course
                studentChallenge.challengeID = challenge
                studentChallenge.startTimestamp = startTime
                studentChallenge.endTimestamp = endTime
                # initially its zero and updated after calculation at the end
                studentChallenge.testScore = 0
                #studentChallenge.instructorFeedback = instructorFeedback
                studentChallenge.save()

                #print(studentChallenge.endTimestamp - studentChallenge.startTimestamp)

                sessionDict = request.session[attemptId]
                if not sessionDict:
                    context_dict['errorName'] = "Challenge not begun"
                    context_dict['errorMessage'] = "An attempt to submit challenge "+challenge.challengeName+" has occurred, but this system has " + \
                        "no record of that challenge begin taken."
                    return render(request, "Students/ChallengeError.html", context_dict)
                    print("challenge result requested for challenge not begun.")

                # We add a one minute fudge factor to account for things like network delays
                if (endTime - startTime).total_seconds() > (challenge.timeLimit+1) * 60:
                    context_dict['errorName'] = "Time Expired"
                    context_dict['errorMessage'] = "Time expired prior to the submission of this challenge."
                    return render(request, "Students/ChallengeError.html", context_dict)

                questions = sessionDict['questions']
                context_dict["questionCount"] = len(questions)
                totalStudentScore = 0
                totalPossibleScore = 0

                for question in questions:
                    questionType = question['type']
                    studentAnswerList = questionTypeFunctions[questionType]["makeAnswerList"](
                        question, request.POST)
                    question = questionTypeFunctions[questionType]["studentAnswersAndGrades"](
                        question, studentAnswerList)
                    totalStudentScore += question['user_points']
                    totalPossibleScore += question['total_points']
                    
                    if 'seed' in question:
                        seed = question['seed']
                    else:
                        seed = 0
                    studentChallengeQuestion = saveChallengeQuestion(
                        studentChallenge, question['questionID'], question['user_points'], question['total_points'], "", seed)

                    static_question = StaticQuestions.objects.get(questionID=question['questionID'])

                    # Award skills if the answer was correct.
                    if question['user_points'] == question['total_points']:
                        question['feedback'] = static_question.correctAnswerFeedback
                        saveSkillPoints(
                            question['id'], currentCourse, studentId, studentChallengeQuestion)
                    else:
                        question['feedback'] = static_question.incorrectAnswerFeedback

                    for studentAnswer in studentAnswerList:
                        studentChallengeAnswers = StudentChallengeAnswers()
                        studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                        studentChallengeAnswers.studentAnswer = studentAnswer
                        studentChallengeAnswers.save()

                # The sort on the next line should be unnecessary, but better safe than sorry
                context_dict['questions'] = sorted(
                    questions, key=lambda q: q['index'])
                context_dict['total_user_points'] = totalStudentScore
                context_dict['total_possible_points'] = totalPossibleScore

                studentChallenge.testScore = totalStudentScore
                studentChallenge.save()

                # In case things have been changed since the last time it was taken or this is first time anyone has taken
                if challenge.totalScore != totalPossibleScore:
                    challenge.totalScore = totalPossibleScore
                    challenge.save()

                register_event(Event.endChallenge, request,
                               studentId, challengeId)
                register_event(Event.leaderboardUpdate,
                               request, studentId, challengeId)
                updateLeaderboard(course)

                print("studentChallege ", studentChallenge)
                print("studentId ", studentId)

                if is_duel:
                    context_dict = duel_challenge_evaluate(
                        studentId, currentCourse, duel_challenge, context_dict)
                elif is_call_out:

                    call_out_part = CalloutParticipants.objects.get(
                        pk=int(request.POST["calloutPartID"]))
                    call_out = call_out_part.calloutID
                    sender_stat = CalloutStats.objects.get(
                        calloutID=call_out, studentID=call_out.sender)
                    call_out_participant = CalloutParticipants.objects.get(
                        calloutID=call_out, participantID=studentId)
                    participant_chall = StudentChallenges.objects.filter(
                        challengeID=call_out.challengeID, studentID=studentId, courseID=currentCourse).latest('testScore')
                    evaluator(call_out, sender_stat, call_out_participant, studentId,
                              currentCourse, participant_chall, already_taken=False)
                
                # At this point, we've gotten all the information out of the entry in the session for this challenge.
                # To save space, we are going to remove it.  Otherwise, the number of session entries keeps piling up until
                # the session size gets ridiculous.
                if attemptId in request.session:
                    # Condition should always be true, but I'm being extra cautious
                    del request.session[attemptId]
                # We also take this time to clean up any session entries from challenges which got started and never finished and are
                # at least a month old.
                remove_old_challenge_session_entries(request.session)

        if request.GET:

            if 'warmUp' in request.GET:
                context_dict['warmUp'] = True
            if 'all' in request.GET:
                context_dict['all'] = True
            if 'classAchievements' in request.GET:
                context_dict['classAchievements'] = True
            if 'view' in request.GET:
                context_dict['view'] = True
            if 'duelID' in request.GET:
                context_dict['isDuel'] = True
                context_dict['duelID'] = request.GET['duelID']
            elif 'calloutPartID' in request.GET:
                context_dict['isCallout'] = True
                context_dict['calloutPartID'] = request.POST['calloutPartID']

            if 'studentChallengeID' in request.GET:
                studentChallengeId = request.GET['studentChallengeID']
                context_dict['studentChallengeID'] = request.GET['studentChallengeID']
            else:
                student = context_dict['student']
                challenge = Challenges.objects.get(
                    pk=int(request.GET['challengeID']))
                studentChallengeId = StudentChallenges.objects.filter(
                    studentID=student, courseID=currentCourse, challengeID=challenge.challengeID)

            challengeId = request.GET['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeId))
            context_dict['challengeName'] = challenge.challengeName
            context_dict['challengeID'] = request.GET['challengeID']

            # Get all the questions for this challenge (AH)
            questionObjects = []
            challengeQuestions = []
            challenge_questions = StudentChallengeQuestions.objects.filter(
                studentChallengeID=studentChallengeId)
            for challenge_question in challenge_questions:
                questionObjects.append(challenge_question.questionID)
                challengeQuestions.append(challenge_question)

            # Find the total student score for this challenge attemmpt (AH)
            studentChallenges = StudentChallenges.objects.filter(
                courseID=currentCourse, challengeID=challengeId, studentChallengeID=studentChallengeId)
            for Schallenges in studentChallenges:
                if int(Schallenges.challengeID.challengeID) == int(challengeId):
                    totalStudentScore = Schallenges.testScore
            context_dict['total_user_points'] = totalStudentScore

            # Next few lines of code is very similar to POST (AH)
            questions = []
            for i, challenge_question in zip(range(0, len(questionObjects)), challengeQuestions):
                q = questionObjects[i]

                studentChallengeQuestion = StudentChallengeQuestions.objects.get(
                    studentChallengeID=studentChallengeId, questionID=q.questionID)

                questDict = questionTypeFunctions[q.type]["makeqdict"](
                    q, i, challengeId, studentChallengeQuestion)
                questDict['total_points'] = challenge_questions.get(
                    questionID=q).questionTotal


                studentAnswers = StudentChallengeAnswers.objects.filter(
                    studentChallengeQuestionID=challenge_question)
                questDict = questionTypeFunctions[q.type]["studentAnswersAndGrades"](
                    questDict, [sa.studentAnswer for sa in studentAnswers])
                questions.append(questDict)

            context_dict["questionCount"] = len(questions)
            context_dict['total_possible_points'] = sum(
                [question['total_points'] for question in questions])

            # The sort on the next line should be unnecessary, but better safe than sorry
            context_dict['questions'] = sorted(
                questions, key=lambda q: q['index'])
            context_dict['ckeditor'] = config_ck_editor()

    return render(request, 'Students/ChallengeResults.html', context_dict)
