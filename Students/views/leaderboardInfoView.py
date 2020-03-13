#  GGM
#  11/26/2018

from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from Students.views.utils import studentInitialContextDict
from Badges.models import LeaderboardsConfig, CourseConfigParams


@login_required
def leaderboardInfoView(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
     
    xpPercentage = ccparams.xpWeightSP
    xpSerious = ccparams.xpWeightSChallenge
    xpWarmup = ccparams.xpWeightWChallenge
    xpActivity = ccparams.xpWeightAPoints
    
    if request.method == 'GET':
        leaderboards = []
        leaderboard_range = []
        leaderboards = LeaderboardsConfig.objects.filter(courseID=currentCourse).order_by("leaderboardName")
        
        leaderboards = list(leaderboards)
        
        for leaderboard in leaderboards:
            if(leaderboard.isXpLeaderboard):
                leaderboard_range.append((leaderboard.leaderboardName, "The ranking in this leaderboard is based on the experience points(XP). The XP score is composed of Skill points: " + str(xpPercentage) +"% Serious Challenges: " +  str(xpSerious) + "% Warmup Challenges: " + str(xpWarmup) + "% Activity Points: " + str(xpActivity) +"%"))
            else:
                leaderboard_range.append((leaderboard.leaderboardName, leaderboard.leaderboardDescription))
            
        leaderboard_range = sorted(leaderboard_range, key=lambda kv: kv[0].lower())
        
        context_dict['leaderboard_range'] = leaderboard_range
    return render(request,'Students/LeaderboardInfo.html',context_dict)