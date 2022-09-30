'''
Created on April 22, 2022 by Phillip Collins (based on createPlayerType by Charles)
#Updated The order of the fields to match the templates
@author: Charles + Phillip Collins
'''
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils import timezone

from Badges.models import CourseConfigParams, PlayerType
from Badges.systemVariables import logger
from Instructors.views.utils import initialContextDict, str_datetime_to_local
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def viewPlayerTypeView(request):

    context_dict, currentCourse = initialContextDict(request)

    if request.POST:
        if request.POST['playerTypeID']:
            playerType = PlayerType.objects.filter(pk=int(request.POST['playerTypeID']),course=currentCourse).first()
        else:
            # Create new player type
            playerType = PlayerType()
            playerType.course = currentCourse
        playerType.name = request.POST['name']
        playerType.badgesUsed = "badgesUsed" in request.POST
        playerType.levelingUsed = "levelingUsed" in request.POST
        playerType.progressBarUsed = "progressBarUsed" in request.POST   
        playerType.goalsUsed = "goalsUsed" in request.POST
        playerType.virtualCurrencyUsed = "virtualCurrencyUsed" in request.POST
        playerType.leaderboardUsed = "leaderboardUsed" in request.POST
        playerType.classmatesChallenges = "classmatesChallenges" in request.POST
        playerType.betVC = "betVC" in request.POST
        playerType.displayAchievementPage= "displayAchievementPage" in request.POST
        playerType.xpLeaderboardUsed = "xpLeaderboardUsed" in request.POST 
        playerType.xpDisplayUsed = "xpDisplayUsed" in request.POST
        # Student Starting Page
        playerType.displayStudentStartPageSummary = request.POST.get(
            'displayStudentStartPageSummary') 


        
        playerType.save()
        return redirect('/oneUp/instructors/PlayerTypeList')
                
    elif request.method == 'GET':
        #Filter by ID from list page
        if 'playerTypeID' in request.GET:
            playerType = PlayerType.objects.filter(pk=int(request.GET['playerTypeID']),course=currentCourse).first()
            context_dict['name'] = playerType.name
            context_dict['playerTypeID'] = playerType.pk
            context_dict['badgesUsed'] = playerType.badgesUsed
            context_dict['levelingUsed'] = playerType.levelingUsed
            context_dict['classmatesChallenges'] = playerType.classmatesChallenges
            context_dict['betVC'] = playerType.betVC
            context_dict['progressBarUsed'] = playerType.progressBarUsed
            context_dict['displayAchievementPage'] = playerType.displayAchievementPage
            context_dict['virtualCurrencyUsed'] = playerType.virtualCurrencyUsed
            context_dict['leaderboardUsed'] = playerType.leaderboardUsed
            context_dict['goalsUsed'] = playerType.goalsUsed
            context_dict['displayStudentStartPageSummary'] = playerType.displayStudentStartPageSummary
            context_dict["xpDisplayUsed"] = playerType.xpDisplayUsed
            context_dict["xpLeaderboardUsed"] = playerType.xpLeaderboardUsed
 
        return render(request,'Instructors/ViewPlayerType.html', context_dict)
