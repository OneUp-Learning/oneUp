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
    ccparams.xpCalculateSeriousByMaxScore
    ccparams.xpCalculateWarmupByMaxScore

    XpCalculationString = ""
    if(ccparams.xpCalculateWarmupByMaxScore):
        xpCalculationString = " Warmup Challenges are calculated via Maximum score of each Challenge."
    else:
        xpCalculationString = " Warmup Challenges are calculated via First attempt of each Challenge."
    if(ccparams.xpCalculateSeriousByMaxScore):
        xpCalculationString += " Serious Challenges are calculated via Maxiumum score of each Challenge."
    else:
        xpCalculationString += " Serious Challenges are calculated via First attempt of each Challenge."
    
    
    if request.method == 'GET':
        leaderboards = []
        leaderboard_range = []
        leaderboards = LeaderboardsConfig.objects.filter(courseID=currentCourse).order_by("leaderboardName")
        
        leaderboards = list(leaderboards)
        
        for leaderboard in leaderboards:
            if(leaderboard.isXpLeaderboard):
                leaderboard_range.append((leaderboard.leaderboardName, "The ranking in this leaderboard is based on the experience points(XP). The XP score is composed of " + str(xpPercentage) +"% Skill points, "  + str(xpSerious) +"% Serious Challenge points, "+ str(xpWarmup) + "% Warmup Challenge points, " + str(xpActivity) + "% Activity points." + xpCalculationString))
            else:
                leaderboard_range.append((leaderboard.leaderboardName, leaderboard.leaderboardDescription))
            
        leaderboard_range = sorted(leaderboard_range, key=lambda kv: kv[0].lower())
        
        context_dict['leaderboard_range'] = leaderboard_range
    return render(request,'Students/LeaderboardInfo.html',context_dict)