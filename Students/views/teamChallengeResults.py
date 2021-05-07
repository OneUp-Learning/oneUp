from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from Students.models import (TeamChallenges, TeamStudents, TeamChallengeAnswers, TeamChallengeQuestions)
from Instructors.models import Challenges
from Students.views.utils import studentInitialContextDict
from Instructors.views.utils import current_utctime
@login_required
def teamChallengeResults(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    team_challenges = Challenges.objects.filter(courseID=currentCourse, isTeamChallenge=True)
    
    challenges = []
    for tc in team_challenges:
        item = {
            'challengeID':tc.challengeID,
            'challengeName':tc.challengeName
        }
        challenges.append(item)

    context_dict['challenges'] = sorted(challenges, key = lambda item:item['challengeID'],reverse=True)

    if 'POST' in request.method:

        challengeID = request.POST.get('selectedTeamChallenge')
        if challengeID and challengeID != 'all':
            team_challenges = team_challenges.filter(challengeID=challengeID)
            context_dict['selectedChallengeID'] = int(challengeID)
    
    challenge_results = []

    for challenge in team_challenges:

        attempts = TeamChallenges.objects.filter(challengeID=challenge.challengeID, courseID=currentCourse)
        
        item = {
            'rankings':getBestTeamResult(attempts)[:4],
            'challengeName':challenge.challengeName
        }
        if challenge.startTimestamp <= current_utctime():
            challenge_results.append(item)

    context_dict['challengeResults'] = challenge_results

    return render(request, 'Students/TeamChallengeResults.html', context_dict)

def getBestTeamResult(attempts):
    ranking = {}

    for attempt in attempts:
        best_attempt = ranking.get(attempt.teamID.teamID)
        new_attempt = {
                'attempt':attempt,
                'time':attempt.endTimestamp,
                'score':attempt.testScore,
                'teamName':attempt.teamID.teamName,
                'avatar':attempt.teamID.avatarImage
            }
        if not best_attempt:
            ranking[attempt.teamID.teamID] = new_attempt

        else: 
            if attempt.testScore > best_attempt['score']:
                ranking[attempt.teamID.teamID] = new_attempt

            elif attempt.testScore == best_attempt['score'] and attempt.endTimestamp < best_attempt['time']:
                ranking[attempt.teamID.teamID] = new_attempt
    
    return list({k:v for k, v in sorted(ranking.items(), key=lambda item: (item[1]['attempt'].testScore, -item[1]['time'].timestamp()), reverse=True)}.items())
    
