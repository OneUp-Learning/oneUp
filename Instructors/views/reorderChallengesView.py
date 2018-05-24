'''
Created on February 03, 2018

@author: DD
'''

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Challenges
from Instructors.views import utils
from Instructors.constants import unassigned_problems_challenge_name

@login_required
def reorderChallenges(request):
 
    context_dict,currentCourse = utils.initialContextDict(request)
            
    if request.POST: 
        if request.POST['challengeType']:
            chall_type = request.POST['challengeType'] 

            if chall_type == 'Warmup':          
                challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False)
            else:
                challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
    
            for challenge in challenges:
                if challenge.challengeName != unassigned_problems_challenge_name:
                    challenge.challengePosition = request.POST[str(challenge.challengeID)]
                    challenge.save()

    if chall_type == 'Warmup':    
        return redirect('/oneUp/instructors/warmUpChallengeList')
    else:
        return redirect('/oneUp/instructors/challengesList')