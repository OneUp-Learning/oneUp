'''
Created on Jun 15, 2021
#Updated The order of the fields to match the templates
@author: Charles
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
def createPlayerTypeView(request):

    context_dict, currentCourse = initialContextDict(request)

    if request.POST:
        if request.POST['playerTypeID']:
            print("--> POST Edit Mode")
            playerType = PlayerType.objects.filter(pk=int(request.POST['playerTypeID']),course=currentCourse).first()
            print("POST Edit Mode",playerType)
        else:
            # Create new player type
            print('NEW')
            playerType = PlayerType()
            playerType.course = currentCourse
        playerType.name = request.POST['name']
        playerType.badgesUsed = "badgesUsed" in request.POST
        playerType.levelingUsed = "levelingUsed" in request.POST
        playerType.progressBarUsed = "progressBarUsed" in request.POST   
        playerType.goalsUsed = "goalsUsed" in request.POST
        playerType.virtualCurrencyUsed = "virtualCurrencyUsed" in request.POST
        playerType.leaderboardUsed = "leaderboardUsed" in request.POST
        playerType.classmateChallenges = "classmateChallenges" in request.POST
        playerType.displayAchievementPage= "displayAchievementPage" in request.POST
        playerType.displayStudentStartPageSummary = 'displayStartPageSummary' in request.POST
        


        
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
            context_dict['classmateChallenges'] = playerType.classmatesChallenges
            context_dict['progressBarUsed'] = playerType.progressBarUsed
            
            context_dict['displayAchievementPage'] = playerType.displayAchievementPage
            context_dict['virtualCurrencyUsed'] = playerType.virtualCurrencyUsed
            context_dict['leaderboardUsed'] = playerType.leaderboardUsed
            context_dict['goalsUsed'] = playerType.goalsUsed
            context_dict['displayStartPageSummary'] = playerType.displayStudentStartPageSummary
           
 
        return render(request,'Instructors/CreatePlayerType.html', context_dict)
