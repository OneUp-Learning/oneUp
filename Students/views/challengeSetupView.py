from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime, timedelta
import sys

# GGM import Regular Expression, re
import re
import string
import pytz
from Instructors.models import Challenges, Answers, DynamicQuestions, Questions
from Instructors.models import ChallengesQuestions, MatchingAnswers, StaticQuestions
from Students.models import DuelChallenges, CalloutParticipants, StudentAnswerHints, Student
from Instructors.views.utils import localizedDate, current_localtime, datetime_to_local
from Instructors.constants import unlimited_constant
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.enums import Event
from Badges.models import CourseConfigParams
from Instructors.questionTypes import QuestionTypes, staticQuestionTypesSet, dynamicQuestionTypesSet, questionTypeFunctions
from Instructors.lupaQuestion import lupa_available, LupaQuestion, CodeSegment
from Instructors.views.dynamicQuestionView import makeLibs
from locale import currency
from django.db.models.functions.window import Lead
from oneUp.ckeditorUtil import config_ck_editor


def remove_old_challenge_session_entries(session):
    sessionitems = list(session.items())
    for k, v in sessionitems:
        # We want to make sure this really matches an attempt which we added.
        # AttemptIds all have the form "challenge:NUM@DATETIME" where NUM is the actual
        # challenge number and DATETIME is the actual date and time it was started.
        parts = k.split("@")
        if len(parts) == 2:
            challpart = parts[0]
            datepart = parts[1]
            if challpart[:10] == 'challenge:':
                date = datetime.strptime(datepart, "%m/%d/%Y %I:%M:%S %p")
                delta = datetime.utcnow() - date
                if delta.days > 30:
                    del session[k]


def makeSerializableCopyOfDjangoObjectDictionary(obj):
    dict = obj.__dict__.copy()
    # We remove the Django Status object from the dictionary to prevent serialization problems
    dict.pop("_state", None)
    return dict


@login_required
def ChallengeSetup(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    if 'currentCourseID' in request.session:

        questionObjects = []
        sessionDict = {}
        attemptId = ''
        if request.POST:
            if request.POST['challengeId']:
                ccp = CourseConfigParams.objects.get(courseID=currentCourse)
                context_dict['hintsUsed'] = ccp.hintsUsed
                context_dict['questionTypes'] = QuestionTypes

                challengeId = request.POST['challengeId']
                context_dict['challengeID'] = challengeId
                challenge = Challenges.objects.get(
                    pk=int(request.POST['challengeId']))

                if "duelID" in request.POST:
                    duel_id = request.POST['duelID']
                    duel_challenge = DuelChallenges.objects.get(
                        pk=int(duel_id))
                    context_dict['challengeName'] = duel_challenge.duelChallengeName
                    context_dict['isduration'] = True
                    total_time = duel_challenge.acceptTime + \
                        timedelta(minutes=duel_challenge.startTime) + timedelta(
                            minutes=duel_challenge.timeLimit) # *unsure about this one* TODO: convert datetime to local
                    remaing_time = total_time - current_localtime() #timezone.now() # TODONE: Use current localtime
                    difference_minutes = remaing_time.total_seconds()/60.0
                    context_dict['testDuration'] = difference_minutes
                    context_dict['isDuel'] = True
                    context_dict['duelID'] = duel_id
                elif "calloutPartID" in request.POST:
                    call_out_part_id = request.POST['calloutPartID']
                    call_out_part = CalloutParticipants.objects.get(
                        pk=int(call_out_part_id))
                    context_dict['challengeName'] = call_out_part.calloutID.challengeID.challengeName
                    context_dict['isduration'] = True
                    time_left = (datetime_to_local(call_out_part.calloutID.endTime) - current_localtime()).total_seconds() / 60.0 #(call_out_part.calloutID.endTime - timezone.now()).total_seconds() / 60.0 # TODONE: Use current localtime and convert datetime to local
                    context_dict['testDuration'] = time_left
                    context_dict['isCallout'] = True
                    context_dict['calloutPartID'] = call_out_part_id
                else:
                    context_dict['challengeName'] = challenge.challengeName
                    if challenge.timeLimit == unlimited_constant:
                        context_dict['isduration'] = False
                    else:
                        context_dict['isduration'] = True
                    context_dict['testDuration'] = challenge.timeLimit
                    context_dict['isDuel'] = False


                starttimestring = current_localtime().strftime("%m/%d/%Y %I:%M:%S %p")#timezone.localtime(timezone.now()).strftime("%m/%d/%Y %I:%M:%S %p") # TODONE: Use current localtime before format
                context_dict['startTime'] = starttimestring

                attemptId = 'challenge:'+challengeId + '@' + starttimestring
                context_dict['attemptId'] = attemptId

                sessionDict['challengeId'] = challengeId

                if not challenge.isGraded:
                    context_dict['warmUp'] = 1
                else:
                    context_dict['warmUp'] = 0

                # Checks if password was entered correctly
                if challenge.challengePassword != '':
                    if 'password' not in request.POST or request.POST['password'] != challenge.challengePassword:
                        return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)

#                 if challenge.challengeName == "Parsons":
#                     context_dict['questionType'] = 'parsons'
#                     context_dict['questionText'] = "Construct a function by drag&amp;dropping and reordering lines from the left to the right.The constructed function should return True if the parameter is True and return False otherwise."
#                     return render(request,'Students/ChallengeSetup.html', context_dict)

                # GGM changed it so that it will now order by the question position
                # this allows us to easily order by randomization in the future

                if(challenge.isRandomized):
                    # GGM this line is problematic for large data sets
                    challenge_questions = ChallengesQuestions.objects.filter(
                        challengeID=challengeId).order_by('?')
                else:
                    challenge_questions = ChallengesQuestions.objects.filter(
                        challengeID=challengeId).order_by("questionPosition")
                for challenge_question in challenge_questions:
                    questionObjects.append(challenge_question)

                # getting all the question of the challenge except the matching question

                qlist = []
                sessionDict['questions'] = []
                for i in range(0, len(questionObjects)):
                    q = questionObjects[i]
                    qdict = questionTypeFunctions[q.questionID.type]['makeqdict'](
                        q.questionID, i+1, challengeId, q, None)
                    qlist.append(qdict)
                    sessionDict['questions'].append(qdict)

            request.session[attemptId] = sessionDict
            # As we set this one, we also take a quick moment to clean up old ones if needed.
            remove_old_challenge_session_entries(request.session)
            context_dict['attemptId'] = attemptId
            context_dict['question_range'] = zip(
                range(1, len(questionObjects)+1), qlist)
            print("contents of the qlist", qlist)
            context_dict['question_ids'] = [i for i in range(1, len(questionObjects)+1)]

        register_event(Event.startChallenge, request, None, challengeId)
        print("Registered Event: Start Challenge Event, Student: student in the request, Challenge: " + challengeId)

        context_dict['ckeditor'] = config_ck_editor()

        dumpUnusedHints(Student.objects.get(user=request.user))
    return render(request, 'Students/ChallengeSetup.html', context_dict)

#we have to dump out the unused hints:
#unused hints are defined by hints that do not have a studentchallengeQuestions foreign key attached
#if we leave them in it causes system instability with garbage data lurking around
#we must dump any that exist for the user to ensure accurate reporting even if they miss submitting a challenge
#but they have submitted already some hint requests
#hints that are used properly have a studentChallengeQuestions foreign key
def dumpUnusedHints(student):
    studentAnswerHints = StudentAnswerHints.objects.filter(studentID=student, studentChallengeQuestionID__isnull=True)
    if(len(studentAnswerHints) > 0):
        #dump the hints that didnt get attached to anything
        for studentAnswerHint in studentAnswerHints:
            studentAnswerHint.delete()
