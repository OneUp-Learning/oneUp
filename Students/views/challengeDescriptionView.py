import datetime
from django.shortcuts import render, redirect
from Instructors.models import Challenges
from Instructors.views.utils import localizedDate, current_localtime, datetime_to_local
from Instructors.constants import unlimited_constant
from Students.models import Student, StudentChallenges, DuelChallenges, CalloutParticipants
from Students.views.utils import studentInitialContextDict
from django.db.models import Q
from time import strftime
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

from django.utils import timezone

@login_required
def ChallengeDescription(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict, currentCourse = studentInitialContextDict(request)
    if 'currentCourseID' in request.session:
        chall_ID = []
        chall_Name = []
        currentTime = timezone.now() # TODO: Use current localtime
        string_attributes = ['challengeName', 'courseID', 'isGraded',  # 'challengeCategory','timeLimit','numberAttempts',
                             'challengeAuthor',
                             'displayCorrectAnswer', 'displayCorrectAnswerFeedback', 'displayIncorrectAnswerFeedback',
                             'challengeDifficulty', 'challengePassword', 'isVisible']  # Added challengePassword AH

        challenges = Challenges.objects.filter(courseID=currentCourse,  isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(
            hasStartTimestamp=False), Q(endTimestamp__gt=currentTime) | Q(hasEndTimestamp=False))

        if request.GET:

            # Getting the challenge information which the student has selected
            if request.GET['challengeID']:
                # studentId = 1; # for now student id is 1 as there is no login table.. else studentd id will be the login ID that we get from the cookie or session

                # Duel flag
                is_duel = False

                # Callout flag
                is_callout = False

                if 'isWarmup' in request.GET:
                    context_dict['isWarmup'] = request.GET['isWarmup']

                    if 'duelID' in request.GET:
                        duel_id = request.GET['duelID']
                        context_dict['duelID'] = duel_id
                        is_duel = True
                        context_dict['isDuel'] = is_duel
                    elif 'calloutPartID' in request.GET:
                        is_callout = True
                        callout_part_id = request.GET['calloutPartID']
                        context_dict['calloutPartID'] = callout_part_id
                        context_dict['isCallout'] = is_callout

                else:
                    context_dict['isWarmup'] = False

                studentId = Student.objects.get(user=request.user)

                if is_duel:
                    duel_challenge = DuelChallenges.objects.get(
                        pk=int(duel_id))
                    challenge = duel_challenge.challengeID
                    challengeId = challenge.challengeID
                elif is_callout:
                    call_out_part = CalloutParticipants.objects.get(
                        pk=int(callout_part_id))
                    challenge = call_out_part.calloutID.challengeID
                    challengeId = challenge.challengeID
                    context_dict['calloutPartID'] = call_out_part.id
                    context_dict['participantID'] = studentId.user.id
                else:
                    challengeId = request.GET['challengeID']
                    challenge = Challenges.objects.get(pk=int(challengeId))

                if challenge in challenges:
                    context_dict['available'] = "This challenge can be taken"
                else:
                    context_dict['unAvailable'] = "This challenge can not be taken at this time"

                data = getattr(challenge, 'timeLimit')
                if is_duel:
                    total_time = datetime_to_local(duel_challenge.acceptTime) + \
                        timedelta(minutes=duel_challenge.startTime) + timedelta(
                            minutes=duel_challenge.timeLimit)
                    remaing_time = remaing_time = total_time-timezone.now() # TODO: Use current localtime
                    difference_minutes = remaing_time.total_seconds()/60.0
                    context_dict['timeLimit'] = ("%.2f" % difference_minutes)
                    if difference_minutes <= 0:
                        return redirect('/oneUp/students/DuelChallengeDescription?duelChallengeID=' +
                                        str(duel_challenge.duelChallengeID))
                elif is_callout:
                    time_left = (call_out_part.calloutID.endTime -
                                 timezone.now()).total_seconds() / 60.0 # TODO: Use current localtime and convert datetime to local
                    context_dict['timeLimit'] = ("%.2f" % time_left)
                    if time_left <= 0:
                        return redirect('/oneUp/students/CalloutDescription?call_out_participant_id=' + str(call_out_part.id) + '&participant_id=' + str(call_out_part.participantID.user.id))
                elif data == unlimited_constant:
                    context_dict['timeLimit'] = "None"
                else:
                    context_dict['timeLimit'] = data

                data = getattr(challenge, 'numberAttempts')
                if data == unlimited_constant:
                    context_dict['numberAttempts'] = "Unlimited"
                else:
                    context_dict['numberAttempts'] = data

                context_dict['challengeID'] = challengeId
                for attr in string_attributes:
                    if attr == 'challengeDifficulty':
                        val = getattr(challenge, attr)
                        if val == "":
                            context_dict[attr] = "Unspecified"
                        else:
                            context_dict[attr] = val
                    else:
                        context_dict[attr] = getattr(challenge, attr)

                # override challenge name by duel challenge name if duel challenge is true
                if is_duel:
                    context_dict['challengeName'] = duel_challenge.duelChallengeName

                total_attempts = challenge.numberAttempts
                if data == unlimited_constant:
                    context_dict['more_attempts'] = "Unlimited"
                else:
                    # getting the number of attempts to check if the student is out of attempts
                    num_student_attempts = StudentChallenges.objects.filter(
                        studentID=studentId, challengeID=challengeId).count()

                    if num_student_attempts < (int(total_attempts) - 1):
                        # student has more than one attempt
                        context_dict['more_attempts'] = '' + \
                            str(int(total_attempts) - num_student_attempts) + ''

                    elif num_student_attempts == (int(total_attempts) - 1):
                        # last attempt of the student
                        context_dict['last_attempt'] = 'This is your last attempt!!!'

                    elif num_student_attempts > (int(total_attempts) - 1):
                        # no more attempts left
                        context_dict['no_attempt'] = "Sorry!! You don't have any more attempts left"

    return render(request, 'Students/ChallengeDescription.html', context_dict)
