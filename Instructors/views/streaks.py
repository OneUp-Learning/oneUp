'''
Created on January 18, 2019

@author: Gerardo Gonzalez
'''

from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.template.defaultfilters import default
from django.template.context_processors import request
from oneUp.decorators import instructorsCheck
from Instructors.models import StreakConfiguration, Streaks
from Badges.models import BadgesInfo

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def streaks(request):
    context_dict, currentCourse = initialContextDict(request)
    streak = Streaks()
    if request.method == 'GET':
        streaksList = []
        streaks= Streaks.objects.filter(courseID=currentCourse)
        index = 0
        for streak in streaks:
            #streakType 0 is attendance
            #streakType 1 is challenge
            
            #award type 0 is virtual currency
            #award type 1 is badge
            if streak.streakType == 0:
                streakType = "Attendance"
            if streak.streakType == 1:
                streakType = "Challenge"
            if streak.awardType == 0:
                streakAwardType = "Virtual Currency"
            if streak.awardType == 1:
                streakAwardType = "Badge"
            
            streaksList.append((index, streak.streakID, streakType, streakAwardType, streak.vcAwardAmount, 
                               streak.awardID, streak.streakLength, streak.streakDescription, streak.resetStreak))
            index +=1
        context_dict['streaksList'] =  streaksList
    return render(request,'Instructors/Streaks.html', context_dict)


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def streakConfig(request):
    context_dict, currentCourse = initialContextDict(request)
    if request.method == 'GET':
        badgesList = []
        badges = BadgesInfo.objects.filter(courseID=currentCourse)
        
        for badge in badges:
            badgesList.append((badge.badgeID, badge.badgeName, badge.badgeImage))
        context_dict['badges'] = badgesList
        
        if 'streakID' in request.GET:
            streakId = request.GET['streakID']
            if Streaks.objects.filter(streakID=streakId, courseID=currentCourse).exists():
                    streak = Streaks.objects.filter(streakID=streakId, courseID=currentCourse)[0]
                    context_dict['streakID'] = streak.streakID
                    context_dict['streakDescription'] = streak.streakDescription
                    context_dict['streakLength'] = streak.streakLength
                    context_dict['virtualCurrency'] = streak.vcAwardAmount
                    context_dict['checkbox'] = streak.resetStreak
                    context_dict['badgeID'] = streak.awardID
                    
        return render(request, 'Instructors/StreakConfig.html', context_dict)
        
    if request.method == 'POST':
        print("post")
        if 'streakID' in request.POST:
            if request.POST['streakID'] != '':
                print("streakID", request.POST['streakID'])
                streakID = request.POST['streakID']
                if Streaks.objects.filter(streakID=streakID, courseID=currentCourse).exists():
                    streak = Streaks.objects.filter(streakID=streakID, courseID=currentCourse)[0]
                    
            else:
                streak = Streaks()
        else:
            streak = Streaks()
        
        streak.courseID = currentCourse
        if 'streakDescription' in request.POST:
            streak.streakDescription = request.POST['streakDescription']
        if 'streakType' in request.POST:
            #streakType 0 is attendance
            #streakType 1 is challenge
            streak.streakType = request.POST['streakType']
        if 'awardType' in request.POST:
            #award type 0 is virtual currency
            #award type 1 is badge
            streak.awardType = request.POST['awardType']
        if 'streakLength' in request.POST:
            streak.streakLength = request.POST['streakLength']
        if 'virtualCurrency' in request.POST:
            streak.vcAwardAmount = request.POST['virtualCurrency']
        if 'badgeID' in request.POST:
            print("badgeID",request.POST['badgeID'])
            streak.awardID = request.POST['badgeID']
        if 'resetStreak' in request.POST:
            if int(request.POST['resetStreak']):
                streak.resetStreak = True
            else:
                streak.resetStreak = False
        streak.save()
        return redirect('/oneUp/instructors/streaks')
        
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def streakDelete(request):  
    context_dict, currentCourse = initialContextDict(request)
    if request.POST:
        if 'streakID' in request.POST:
            streakId = request.POST['streakID']
            if Streaks.objects.filter(streakID=streakId, courseID=currentCourse).exists():
                    streak = Streaks.objects.filter(streakID=streakId, courseID=currentCourse)[0]
                    streak.delete()
        return redirect('/oneUp/instructors/streaks')


## we must delete and recreate the periodic event or it will break
def createPeriodicTasksForObjects(leaderboards, oldPeriodicVariableForLeaderboard):
    leaderboardToOldPeriodicVariableDict = dict(zip(leaderboards, oldPeriodicVariableForLeaderboard))
    boolNoOldVariable = False

    if len(leaderboardToOldPeriodicVariableDict):
        leaderboardObjects = leaderboardToOldPeriodicVariableDict
        boolNoOldVariable = True
    else:
        leaderboardObjects = leaderboards
         
    for leaderboard in leaderboardObjects:
        if not leaderboard.isContinous:
            if not boolNoOldVariable:
                delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
            else:
                delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboardToOldPeriodicVariableDict[leaderboard], award_type="leaderboard", course=leaderboard.courseID)
            leaderboard.periodicTask = setup_periodic_leaderboard(leaderboard_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, course=leaderboard.courseID, period_index=leaderboard.timePeriodUpdateInterval,  number_of_top_students=leaderboard.numStudentsDisplayed, threshold=1, operator_type='>', is_random=None)
            leaderboard.save()

def deleteLeaderboardConfigObjects(leaderboards):
    for leaderboardObjID in leaderboards:
        leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(leaderboardObjID))
        if leaderboard.periodicVariable != 0:
            delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
        leaderboard.delete()