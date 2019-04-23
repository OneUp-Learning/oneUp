import datetime
from django.shortcuts import render
from Instructors.models import Challenges
from Instructors.views.utils import utcDate
from Instructors.constants import default_time_str, unlimited_constant
from Students.models import Student, StudentChallenges, DuelChallenges
from Students.views.utils import studentInitialContextDict
from django.db.models import Q
from time import strftime
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta


@login_required
def ChallengeDescription(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict, currentCourse = studentInitialContextDict(request)
    print("request", request)
    if 'currentCourseID' in request.session:
        chall_ID = []
        chall_Name = []
        defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        currentTime = utcDate()
        string_attributes = ['challengeName', 'courseID', 'isGraded',  # 'challengeCategory','timeLimit','numberAttempts',
                             'challengeAuthor',
                             'displayCorrectAnswer', 'displayCorrectAnswerFeedback', 'displayIncorrectAnswerFeedback',
                             'challengeDifficulty', 'challengePassword', 'isVisible']  # Added challengePassword AH

        challenges = Challenges.objects.filter(courseID=currentCourse,  isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(
            startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))

        if request.GET:

            # Getting the challenge information which the student has selected
            if request.GET['challengeID']:
                # studentId = 1; # for now student id is 1 as there is no login table.. else studentd id will be the login ID that we get from the cookie or session
                print("Context Dict", context_dict)

                # Duel flag
                is_duel = False

                if 'isWarmup' in request.GET:
                    context_dict['isWarmup'] = request.GET['isWarmup']

                    if 'duelID' in request.GET:
                        duel_id = request.GET['duelID']
                        context_dict['duelID'] = duel_id
                        is_duel = True
                        context_dict['isDuel'] = is_duel

                else:
                    context_dict['isWarmup'] = False

                studentId = Student.objects.get(user=request.user)

                if is_duel:
                    duel_challenge = DuelChallenges.objects.get(
                        pk=int(duel_id))
                    challenge = duel_challenge.challengeID
                    challengeId = challenge.challengeID

                else:
                    challengeId = request.GET['challengeID']
                    challenge = Challenges.objects.get(pk=int(challengeId))

                if challenge in challenges:
                    context_dict['available'] = "This challenge can be taken"
                else:
                    context_dict['unAvailable'] = "This challenge can not be taken at this time"

                data = getattr(challenge, 'timeLimit')
                if is_duel:
                    total_time = duel_challenge.acceptTime + \
                        timedelta(minutes=duel_challenge.startTime) + timedelta(
                            minutes=duel_challenge.timeLimit)+timedelta(seconds=20)
                    remaing_time = remaing_time = total_time-utcDate()
                    difference_minutes = remaing_time.total_seconds()/60.0
                    context_dict['timeLimit'] = ("%.2f" % difference_minutes)
                elif data == unlimited_constant:
                    context_dict['timeLimit'] = "None"
                else:
                    context_dict['timeLimit'] = data

                data = getattr(challenge, 'numberAttempts')
                print(str(data))
                if data == unlimited_constant:
                    context_dict['numberAttempts'] = "Unlimited"
                else:
                    context_dict['numberAttempts'] = data

                context_dict['challengeID'] = challengeId
                for attr in string_attributes:
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
