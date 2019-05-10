from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime, timedelta
import sys

# GMM import Regular Expression, re
import re
import string
import pytz
from Instructors.models import Challenges, Answers, DynamicQuestions, Questions
from Instructors.models import ChallengesQuestions, MatchingAnswers, StaticQuestions
from Students.models import DuelChallenges, CalloutParticipants
from Instructors.views.utils import utcDate, localizedDate
from Instructors.constants import unlimited_constant
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.enums import Event
from Instructors.questionTypes import QuestionTypes, staticQuestionTypesSet, dynamicQuestionTypesSet, questionTypeFunctions
from Instructors.lupaQuestion import lupa_available, LupaQuestion, CodeSegment
from Instructors.views.dynamicQuestionView import makeLibs
from locale import currency
from django.db.models.functions.window import Lead
from oneUp.ckeditorUtil import config_ck_editor


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
                            minutes=duel_challenge.timeLimit)+timedelta(seconds=20)
                    remaing_time = total_time-utcDate()
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
                    time_left = (call_out_part.calloutID.endTime -
                                 utcDate()).total_seconds() / 60.0
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

                # starttime = utcDate()
                # context_dict['startTime'] = starttime.strftime("%m/%d/%Y %I:%M:%S %p")

                # Use timezone to convert date to current timzone set in settings.py
                tz = pytz.timezone(request.session['django_timezone'])
                starttime = tz.localize(datetime.now()).astimezone(tz)
                context_dict['startTime'] = starttime.strftime(
                    "%m/%d/%Y %I:%M:%S %p")

                attemptId = 'challenge:'+challengeId + '@' + \
                    starttime.strftime("%m/%d/%Y %I:%M:%S %p")

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
                print("Challenge Questions", challenge_questions)
                for challenge_question in challenge_questions:
                    questionObjects.append(challenge_question.questionID)

                # getting all the question of the challenge except the matching question

                qlist = []
                sessionDict['questions'] = []
                for i in range(0, len(questionObjects)):
                    q = questionObjects[i]
                    qdict = questionTypeFunctions[q.type]['makeqdict'](
                        q, i+1, challengeId, None)
                    qlist.append(qdict)
                    sessionDict['questions'].append(qdict)

            request.session[attemptId] = sessionDict
            print("attemptID = "+attemptId)
            context_dict['question_range'] = zip(
                range(1, len(questionObjects)+1), qlist)

        register_event(Event.startChallenge, request, None, challengeId)
        print("Registered Event: Start Challenge Event, Student: student in the request, Challenge: " + challengeId)

        context_dict['ckeditor'] = config_ck_editor()
    return render(request, 'Students/ChallengeSetup.html', context_dict)
