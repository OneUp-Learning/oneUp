'''
Created on Jun 12, 2014
Updated May/10/2017

@author: iiscs
'''
import math
import re
from datetime import datetime
from decimal import Decimal

import pytz
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from Badges.enums import Event
from Badges.event_utils import updateLeaderboard
from Badges.events import register_event
from Badges.systemVariables import logger
from Badges.tasks import refresh_xp
from Instructors.lupaQuestion import CodeSegment, LupaQuestion, lupa_available
from Instructors.models import (Answers, Challenges, ChallengesQuestions,
                                CorrectAnswers, Courses, DynamicQuestions,
                                MatchingAnswers, Questions, QuestionsSkills,
                                StaticQuestions)
from Instructors.questionTypes import (QuestionTypes, dynamicQuestionTypesSet,
                                       questionTypeFunctions,
                                       staticQuestionTypesSet)
from Instructors.views.dynamicQuestionView import makeLibs
from Instructors.views.utils import current_localtime, str_datetime_to_local
from oneUp.ckeditorUtil import config_ck_editor
from Students.models import (CalloutParticipants, CalloutStats, DuelChallenges,
                             Student, StudentAnswerHints,
                             StudentChallengeAnswers,
                             StudentChallengeQuestions, StudentChallenges,
                             StudentCourseSkills)
from Students.views.calloutsView import evaluator
from Students.views.challengeSetupView import (
    makeSerializableCopyOfDjangoObjectDictionary,
    remove_old_challenge_session_entries)
from Students.views.duelChallengeView import duel_challenge_evaluate
from Students.views.utils import studentInitialContextDict


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
                context_dict['challengeID'] = challengeId
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
                    #print("warmUp")
                    context_dict['warmUp'] = 1
                    context_dict['isWarmUp'] = True

                print("Start Time: "+request.POST['startTime'])
                startTime = str_datetime_to_local(request.POST['startTime'], to_format= "%m/%d/%Y %I:%M:%S %p")
                # end time of the test is the current time when it is navigated to this page
                endTime = current_localtime()
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
                questions = placeHintIDIntoQuestionDict(questions, request)

                for question in questions:
                    questionType = question['type']
                    studentAnswerList = questionTypeFunctions[questionType]["makeAnswerList"](
                        question, request.POST)
                    question = questionTypeFunctions[questionType]["studentAnswersAndGrades"](
                        question, studentAnswerList)
                    totalStudentScore += question['user_points']
                    totalPossibleScore += question['total_points']

                    studentChallengeQuestion = saveChallengeQuestion(studentChallenge, question)

                    # Award skills if the answer was correct.
                    if question['user_points'] == question['total_points']:
                        saveSkillPoints(question['id'], currentCourse, studentId, studentChallengeQuestion)

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
#                updateLeaderboard(course)
#                ^^^^^ removed for the moment due to being terribly slow.  Should be off-lined or eliminated.

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
                
                # Update student xp
                refresh_xp(context_dict['student_registered_course'])

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
                    studentID=student, courseID=currentCourse, challengeID=challenge.challengeID).first().studentChallengeID
            
            student_challenge = StudentChallenges.objects.get(pk=int(studentChallengeId))

            challengeId = request.GET['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeId))
            context_dict['challengeName'] = challenge.challengeName
            context_dict['challengeID'] = request.GET['challengeID']

            # Get all the questions for this challenge (AH)
            challengeQuestions = []
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=student_challenge.challengeID)
            for challenge_question in challenge_questions:
                challengeQuestions.append(challenge_question)

            # Find the total student score for this challenge attemmpt (AH)
            # studentChallenges = StudentChallenges.objects.filter(
            #     courseID=currentCourse, challengeID=challengeId, studentChallengeID=studentChallengeId)
            # for Schallenges in studentChallenges:
            #     if int(Schallenges.challengeID.challengeID) == int(challengeId):
            #         totalStudentScore = Schallenges.testScore

            context_dict['total_user_points'] = student_challenge.testScore

            # Next few lines of code is very similar to POST (AH)
            questions = []
            for i in range(0, len(challengeQuestions)):
                challenge_question = challengeQuestions[i]

                studentChallengeQuestion = StudentChallengeQuestions.objects.get(challengeQuestionID=challenge_question, studentChallengeID=student_challenge ,studentChallengeID__studentID=context_dict['student'], studentChallengeID__courseID=currentCourse)
                questDict = questionTypeFunctions[challenge_question.questionID.type]["makeqdict"](
                    challenge_question.questionID, i, challengeId, challenge_question, studentChallengeQuestion)
                questDict['total_points'] = studentChallengeQuestion.questionTotal

                studentAnswers = StudentChallengeAnswers.objects.filter(
                    studentChallengeQuestionID=studentChallengeQuestion)
                questDict = questionTypeFunctions[challenge_question.questionID.type]["studentAnswersAndGrades"](
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

def saveChallengeQuestion(student_challenge, question):
    if 'seed' in question:
        seed = question['seed']
    else:
        seed = 0

    studentChallengeQuestion = StudentChallengeQuestions()
    studentChallengeQuestion.studentChallengeID = student_challenge
    studentChallengeQuestion.questionID = Questions(question['questionID'])
    studentChallengeQuestion.challengeQuestionID = ChallengesQuestions(question['challenge_question_id'])
    studentChallengeQuestion.questionScore = question['user_points']
    studentChallengeQuestion.questionTotal = question['total_points']
    studentChallengeQuestion.usedHint = "False"
    studentChallengeQuestion.seed = seed
    studentChallengeQuestion.save()

    if 'hintID' in question:
        attachStudentHintToStudentChallenge(student_challenge.studentID, question, studentChallengeQuestion)
    return studentChallengeQuestion

#we have to attach student hints to the Challenge
def attachStudentHintToStudentChallenge(studentID, question, student_challenge_question ):
    studentHintExists = StudentAnswerHints.objects.filter(
        studentID=studentID, 
        studentAnswerHintsID=question['hintID'],
        challengeQuestionID=int(question['challenge_question_id'])
    ).exists()

    #first check if the student Hint exists or we're going to cause problems
    if(studentHintExists):
        studentHint = StudentAnswerHints.objects.get(studentID=studentID, studentAnswerHintsID=question['hintID'], challengeQuestionID=question['challenge_question_id'])
        studentHint.studentChallengeQuestionID = student_challenge_question
        studentHint.save()
    
def placeHintIDIntoQuestionDict(questions, request):
    i = 1
    for question in questions:
        hintID = str(i)+'hintID'
        if hintID in request.POST and request.POST[hintID] != '':
            hintID = request.POST[hintID]
            question['hintID'] = hintID
        i += 1
    return questions
