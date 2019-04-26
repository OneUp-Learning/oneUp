'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Badges.models import CourseConfigParams, LeaderboardsConfig
from Students.models import StudentRegisteredCourses
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck   

from Instructors.views.dynamicLeaderboardView import createXPLeaderboard

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def preferencesView(request):

    context_dict, currentCourse = initialContextDict(request)
    
    if request.POST:
        
        if request.POST['ccpID']:
            print("--> POST Edit Mode")
            ccparams = CourseConfigParams.objects.get(pk=int(request.POST['ccpID']))
            print("POST Edit Mode",ccparams)
        else:
            # Create new Config Parameters
            ccparams = CourseConfigParams()
            ccparams.courseID = currentCourse

        # Badges
        ccparams.badgesUsed = "badgesUsed" in request.POST
        if ccparams.badgesUsed == True:    
            ccparams.studCanChangeBadgeVis = "studCanChangeBadgeVis" in request.POST
            ccparams.numBadgesDisplayed = request.POST.get('numBadgesDisplayed')
        else:
            ccparams.studCanChangeBadgeVis =False
            ccparams.numBadgesDisplayed=0

        # Leveling    
        ccparams.levelingUsed = "levelingUsed" in request.POST
        
        # Duels
        ccparams.classmatesChallenges = "classmatesChallenges" in request.POST
        if ccparams.classmatesChallenges:
            ccparams.vcDuel = request.POST.get('vc_duel')
            ccparams.vcCallout = request.POST.get('vc_callout')
            ccparams.vcDuelParticipants = request.POST.get('vc_duel_participants')
            ccparams.vcDuelMaxBet = request.POST.get("vc_duel_max_bet")
        else:
            ccparams.vcDuel = 0
            ccparams.vcCallout = 0
            ccparams.vcDuelParticipants = 0
        ccparams.betVC = "betVC" in request.POST
        
        # Leaderboards
        ccparams.leaderboardUsed = "leaderboardUsed" in request.POST
        if ccparams.leaderboardUsed == True:    
            ccparams.studCanChangeLeaderboardVis = "studCanChangeLeaderboardVis" in request.POST
            ccparams.numStudentsDisplayed = request.POST.get('numStudentsDisplayed')
            # Not being used anywhere
            ccparams.leaderboardUpdateFreq = 1
        else:
            ccparams.studCanChangeLeaderboardVis =False
            ccparams.numStudentsDisplayed = 0
        
        if 'xpLeaderboardID' in request.POST and request.POST['numStudentsDisplayed'] != 0:
            # Create/Edit XP leaderboard (default leaderboard)
            if request.POST['xpLeaderboardID']:
                leaderboard = LeaderboardsConfig.objects.get(leaderboardID=request.POST['xpLeaderboardID'])
            else:
                leaderboard = createXPLeaderboard(currentCourse, request)
            leaderboard.leaderboardDescription = request.POST['leaderboardDescription']
            # numStudentsDisplayed seems redundant as it is in ccparams
            leaderboard.numStudentsDisplayed = int(request.POST['numStudentsDisplayed'])
            leaderboard.isXpLeaderboard = True
            leaderboard.displayOnCourseHomePage = True
            leaderboard.courseID = currentCourse
            leaderboard.save()

        # XP
        ccparams.xpWeightSChallenge = request.POST.get('xpWeightSChallenge')
        ccparams.xpWeightWChallenge = request.POST.get('xpWeightWChallenge')
        ccparams.xpWeightSP = request.POST.get('xpWeightSP')
        ccparams.xpWeightAPoints = request.POST.get('xpWeightAPoints')
        ccparams.xpCalculateSeriousByMaxScore = request.POST.get('xpCalculateSeriousByMaxScore')
        ccparams.xpCalculateWarmupByMaxScore = request.POST.get('xpCalculateWarmupByMaxScore')
        
        # Skills
        ccparams.classSkillsDisplayed = "classSkillsDisplayed" in request.POST
        if ccparams.classSkillsDisplayed == True:
            ccparams.studCanChangeClassSkillsVis = "studCanChangeClassSkillsVis" in request.POST
            ccparams.numStudentBestSkillsDisplayed = request.POST.get('numStudentBestSkillsDisplayed')
        else:
            ccparams.studCanChangeClassSkillsVis = False
            ccparams.numStudentBestSkillsDisplayed = 0
        
        # Virtual Currency
        ccparams.virtualCurrencyUsed  = "virtualCurrencyUsed" in request.POST
        # Should the new currency be added to the previous ot replace it??
        #the first is uncommented below
        ccparams.virtualCurrencyAdded =  request.POST.get('virtualCurrencyAdded')
        #ccparams.virtualCurrencyAdded +=  int(request.POST.get('virtualCurrencyAdded'))
        
        #If students were already added to the class: Add the specified quantity to the account of every student in this class
        st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
        for st_c in st_crs:
            if ccparams.virtualCurrencyAdded:
                st_c.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
                st_c.save()
        
        ccparams.avatarUsed = "avatarUsed" in request.POST
        ccparams.classAverageUsed = "classAverageUsed" in request.POST
        ccparams.studCanChangeclassAverageVis = "studCanChangeclassAverageVis" in request.POST
    
        
        
        ccparams.thresholdToLevelMedium = request.POST.get('thresholdToLevelMedium')
        ccparams.thresholdToLevelDifficulty = request.POST.get('thresholdToLevelDifficulty')
        
        ccparams.streaksUsed = "streaksUsed" in request.POST
        
        ## 4.3.2019  JC
        ccparams.studCanChangeGoal = "studCanChangeGoal" in request.POST
        
        ccparams.save()

        return redirect('/oneUp/instructors/instructorCourseHome',"","")
                
    elif request.method == 'GET':
        
        ccparams = context_dict['ccparams']
            
        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID

            # Badges
            context_dict["badgesUsed"]=ccparams.badgesUsed
            context_dict["numBadgesDisplayed"]=ccparams.numBadgesDisplayed
            context_dict["studCanChangeBadgeVis"]=ccparams.studCanChangeBadgeVis
            
            # Leveling
            context_dict["levelingUsed"]=ccparams.levelingUsed

            # Leaderboard
            context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
            context_dict["leaderboardUpdateFreq"]=ccparams.leaderboardUpdateFreq
            context_dict["studCanChangeLeaderboardVis"]=ccparams.studCanChangeLeaderboardVis
            xpLeaderboard = LeaderboardsConfig.objects.filter(courseID=currentCourse, isXpLeaderboard=True).first()
            if xpLeaderboard:
                context_dict["xpLeaderboardID"] = xpLeaderboard.leaderboardID
                context_dict['leaderboardDescription'] = xpLeaderboard.leaderboardDescription
                # context_dict["numStudentsDisplayed"]= xpLeaderboard.numStudentsDisplayed
            context_dict["numStudentsDisplayed"]=ccparams.numStudentsDisplayed

            # XP
            context_dict["xpWeightSChallenge"] = ccparams.xpWeightSChallenge
            context_dict["xpWeightWChallenge"] = ccparams.xpWeightWChallenge
            context_dict["xpWeightSP"] = ccparams.xpWeightSP
            context_dict["xpWeightAPoints"] = ccparams.xpWeightAPoints
            context_dict["xpCalculateSeriousByMaxScore"] = ccparams.xpCalculateSeriousByMaxScore
            context_dict["xpCalculateWarmupByMaxScore"] = ccparams.xpCalculateWarmupByMaxScore

            # Skills
            context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
            context_dict["studCanChangeClassSkillsVis"]=ccparams.studCanChangeClassSkillsVis
            context_dict["numStudentBestSkillsDisplayed"]=ccparams.numStudentBestSkillsDisplayed

            # Virtual Currency
            context_dict["virtualCurrencyUsed"]=ccparams.virtualCurrencyUsed
            context_dict["virtualCurrencyAdded"]=ccparams.virtualCurrencyAdded

            # Avatars
            context_dict["avatarUsed"]=ccparams.avatarUsed

            # Student Settings
            context_dict["classAverageUsed"]=ccparams.classAverageUsed
            context_dict["studCanChangeclassAverageVis"]=ccparams.studCanChangeclassAverageVis

            # Challenge Difficulty
            context_dict["thresholdToLevelMedium"]=ccparams.thresholdToLevelMedium
            context_dict["thresholdToLevelDifficulty"]=ccparams.thresholdToLevelDifficulty

            # Duels
            context_dict["classmatesChallenges"]=ccparams.classmatesChallenges
            context_dict["vc_callout"] = ccparams.vcCallout
            context_dict["vc_duel"] = ccparams.vcDuel
            context_dict["betVC"] = ccparams.betVC
            context_dict["vc_duel_participants"] = ccparams.vcDuelParticipants
            context_dict["vc_duel_max_bet"] = ccparams.vcDuelMaxBet

            # Streaks
            context_dict["streaksUsed"] = ccparams.streaksUsed
            context_dict["studCanChangeGoal"]=ccparams.studCanChangeGoal
            
 
        return render(request,'Instructors/Preferences.html', context_dict)
    


