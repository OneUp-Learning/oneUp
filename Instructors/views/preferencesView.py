'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Badges.models import CourseConfigParams, LeaderboardsConfig
from Badges.tasks import refresh_xp, recalculate_student_virtual_currency_total_offline
from Instructors.views.dynamicLeaderboardView import createXPLeaderboard
from Instructors.views.utils import initialContextDict
from Instructors.models import InstructorRegisteredCourses
from oneUp.decorators import instructorsCheck
from Students.models import StudentRegisteredCourses, StudentVirtualCurrency


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def preferencesView(request):

    context_dict, currentCourse = initialContextDict(request)


    if request.POST:

        if request.POST['ccpID']:
            print("--> POST Edit Mode")
            ccparams = CourseConfigParams.objects.get(
                pk=int(request.POST['ccpID']))
            print("POST Edit Mode", ccparams)
        else:
            # Creation of course config parameters is when creating a new course
            redirect('/oneUp/instructors/instructorCourseHome', "", "")

        # Badges
        ccparams.badgesUsed = "badgesUsed" in request.POST
        if ccparams.badgesUsed == True:
            ccparams.studCanChangeBadgeVis = "studCanChangeBadgeVis" in request.POST
            ccparams.numBadgesDisplayed = request.POST.get(
                'numBadgesDisplayed')
        else:
            ccparams.studCanChangeBadgeVis = False
            ccparams.numBadgesDisplayed = 0

        # Progress Bar
        ccparams.progressBarUsed = "progressBarUsed" in request.POST
        ccparams.progressBarTotalPoints = request.POST.get(
            'progressBarTotalPoints')
        ccparams.progressBarGroupUsed = "progressBarGroupUsed" in request.POST
        ccparams.progressBarGroupAverage = request.POST.get(
            'progressBarGroupAverage')

        # Student Starting Page
        ccparams.displayStudentStartPageSummary = request.POST.get(
            'displayStudentStartPageSummary')


        # Leveling
        ccparams.levelingUsed = "levelingUsed" in request.POST
        if ccparams.levelingUsed:
            ccparams.levelTo1XP = request.POST.get('levelTo1XP')
            ccparams.nextLevelPercent = request.POST.get('nextLevelPercent')

        # Duels & callouts
        ccparams.classmatesChallenges = "classmatesChallenges" in request.POST
        if ccparams.classmatesChallenges:
            ccparams.vcDuel = request.POST.get('vc_duel')
            ccparams.vcCallout = request.POST.get('vc_callout')
            ccparams.vcDuelParticipants = request.POST.get(
                'vc_duel_participants')
            ccparams.vcDuelMaxBet = request.POST.get("vc_duel_max_bet")
            ccparams.minimumCreditPercentage = request.POST.get('minimumCreditPercent')
        else:
            ccparams.vcDuel = 0
            ccparams.vcCallout = 0
            ccparams.vcDuelParticipants = 0
            ccparams.minimumCreditPercentage = 0
        ccparams.betVC = "betVC" in request.POST
        ccparams.calloutAfterWarmup = "calloutAfterWarmup" in request.POST

        # Leaderboards
        ccparams.leaderboardUsed = "leaderboardUsed" in request.POST
        if ccparams.leaderboardUsed == True:
            ccparams.studCanChangeLeaderboardVis = "studCanChangeLeaderboardVis" in request.POST
            ccparams.numStudentsDisplayed = request.POST.get(
                'numStudentsDisplayed')
            # Not being used anywhere
            ccparams.leaderboardUpdateFreq = 1
        else:
            ccparams.studCanChangeLeaderboardVis = False
            ccparams.numStudentsDisplayed = 0

        if 'xpLeaderboardID' in request.POST and request.POST['numStudentsDisplayed'] != 0:
            # Create/Edit XP leaderboard (default leaderboard)
            if request.POST['xpLeaderboardID']:
                leaderboard = LeaderboardsConfig.objects.get(
                    leaderboardID=request.POST['xpLeaderboardID'])
            else:
                leaderboard = createXPLeaderboard(currentCourse, request)
            #leaderboard.leaderboardDescription = request.POST['leaderboardDescription']
            # numStudentsDisplayed seems redundant as it is in ccparams
            leaderboard.numStudentsDisplayed = int(
                request.POST['numStudentsDisplayed'])
            leaderboard.isXpLeaderboard = True
            leaderboard.displayOnCourseHomePage = True
            leaderboard.courseID = currentCourse
            leaderboard.save()
            
        ccparams.xpLeaderboardUsed = "xpLeaderboardUsed" in request.POST 
        
        # XP
        ccparams.xpWeightSChallenge = request.POST.get('xpWeightSChallenge')
        ccparams.xpWeightWChallenge = request.POST.get('xpWeightWChallenge')
        ccparams.xpWeightSP = request.POST.get('xpWeightSP')
        ccparams.xpWeightAPoints = request.POST.get('xpWeightAPoints')
        ccparams.xpCalculateSeriousByMaxScore = request.POST.get(
            'xpCalculateSeriousByMaxScore')
        ccparams.xpCalculateWarmupByMaxScore = request.POST.get(
            'xpCalculateWarmupByMaxScore')
        ccparams.xpDisplayUsed = "xpDisplayUsed" in request.POST 
        
        # Skills
        ccparams.classSkillsDisplayed = "classSkillsDisplayed" in request.POST
        if ccparams.classSkillsDisplayed == True:
            ccparams.studCanChangeClassSkillsVis = "studCanChangeClassSkillsVis" in request.POST
            ccparams.numStudentBestSkillsDisplayed = request.POST.get(
                'numStudentBestSkillsDisplayed')
        else:
            ccparams.studCanChangeClassSkillsVis = False
            ccparams.numStudentBestSkillsDisplayed = 0

        # Virtual Currency
        ccparams.virtualCurrencyUsed = "virtualCurrencyUsed" in request.POST
        vcaddedString = request.POST.get('virtualCurrencyAdded')
        
        ccparams.classFundEnabled = "classFundEnabled" in request.POST
      
        currentCourse.Donations = request.POST.get("classFundChange")
        
        # Virtual Applause
        ccparams.applauseOn = "applauseOn" in request.POST
      
        
        currentCourse.save()
        if vcaddedString:
            
            vcaddedInt = int(vcaddedString)
            if vcaddedInt != 0:
                ccparams.virtualCurrencyAdded += vcaddedInt
                
                # If students were already added to the class: Add the specified quantity to the account of every student in this class
                st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
                for st_c in st_crs:
                    # We have now switched to the canonical virtual currency amount a student has being determined by their transactions,
                    # so we first add a StudentVirtualCurrency entry to show their gain and then we adjust the virtualCurrencyAmount.
                    createSCVforInstructorGrant(st_c.studentID,currentCourse,vcaddedInt)
                
                    st_c.virtualCurrencyAmount += vcaddedInt
                    st_c.save()
                    recalculate_student_virtual_currency_total_offline(st_c.studentID.pk,currentCourse.pk)

        ccparams.avatarUsed = "avatarUsed" in request.POST
        ccparams.useCustomAvatar = "useCustomAvatar" in request.POST
        
        ccparams.studCanChangeclassAverageVis = "studCanChangeclassAverageVis" in request.POST

        ccparams.contentUnlockingDisplayed = "contentUnlockingDisplayed" in request.POST
        ccparams.debugSystemVariablesDisplayed = "debugSystemVariablesDisplayed" in request.POST

        ccparams.thresholdToLevelMedium = request.POST.get(
            'thresholdToLevelMedium')
        ccparams.thresholdToLevelDifficulty = request.POST.get(
            'thresholdToLevelDifficulty')



        # Goals
        ccparams.goalsUsed = "goalsUsed" in request.POST
        ccparams.studCanChangeGoal = "studCanChangeGoal" in request.POST

        # Adaptation
        ccparams.adaptationUsed = "adaptationUsed" in request.POST

       # moved to course config
       #ccparams.streaksUsed = "streaksUsed" in request.POST
        ccparams.save()

        # Because leaderboard settings might have changed or VC might have been awarded, we recalculate every student's XP after this page is submitted
        # This happens offline, so it won't slow down the page load, but it is a little wasteful.  I'm doing it anyway because we don't expect this page
        # to be used very frequently, so the extra load shouldn't be significant and this way we make sure we don't miss any cases.
        st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
        for st_c in st_crs:
            refresh_xp(st_c)

        return redirect('/oneUp/instructors/instructorCourseHome', "", "")

    elif request.method == 'GET':

        ccparams = context_dict['ccparams']

        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID

            # Badges
            context_dict["badgesUsed"] = ccparams.badgesUsed
            context_dict["numBadgesDisplayed"] = ccparams.numBadgesDisplayed
            context_dict["studCanChangeBadgeVis"] = ccparams.studCanChangeBadgeVis

            # Progress Bar
            context_dict["progressBarUsed"] = ccparams.progressBarUsed
            context_dict["progressBarTotalPoints"] = ccparams.progressBarTotalPoints
            context_dict["progressBarGroupUsed"] = ccparams.progressBarGroupUsed
            context_dict["progressBarGroupAverage"] = ccparams.progressBarGroupAverage

            # Student Start Page
            context_dict["displayStudentStartPageSummary"] = ccparams.displayStudentStartPageSummary

            

            # Leveling
            context_dict["levelingUsed"] = ccparams.levelingUsed
            context_dict["levelTo1XP"] = int(
                ccparams.levelTo1XP) if ccparams.levelTo1XP % 2 == 0 else ccparams.levelTo1XP
            context_dict['nextLevelPercent'] = int(
                ccparams.nextLevelPercent) if ccparams.nextLevelPercent % 2 == 0 else ccparams.nextLevelPercent

            # Leaderboard
            context_dict["leaderboardUsed"] = ccparams.leaderboardUsed
            context_dict["leaderboardUpdateFreq"] = ccparams.leaderboardUpdateFreq
            context_dict["studCanChangeLeaderboardVis"] = ccparams.studCanChangeLeaderboardVis
            xpLeaderboard = LeaderboardsConfig.objects.filter(
                courseID=currentCourse, isXpLeaderboard=True).first()
            if xpLeaderboard:
                context_dict["xpLeaderboardID"] = xpLeaderboard.leaderboardID
                context_dict['leaderboardDescription'] = xpLeaderboard.leaderboardDescription
                # context_dict["numStudentsDisplayed"]= xpLeaderboard.numStudentsDisplayed
            context_dict["numStudentsDisplayed"] = ccparams.numStudentsDisplayed
            context_dict["xpLeaderboardUsed"] = ccparams.xpLeaderboardUsed
          
            # XP
            context_dict["xpWeightSChallenge"] = ccparams.xpWeightSChallenge
            context_dict["xpWeightWChallenge"] = ccparams.xpWeightWChallenge
            context_dict["xpWeightSP"] = ccparams.xpWeightSP
            context_dict["xpWeightAPoints"] = ccparams.xpWeightAPoints
            context_dict["xpCalculateSeriousByMaxScore"] = ccparams.xpCalculateSeriousByMaxScore
            context_dict["xpCalculateWarmupByMaxScore"] = ccparams.xpCalculateWarmupByMaxScore
            context_dict["xpDisplayUsed"] = ccparams.xpDisplayUsed
            
            # Skills
            context_dict["classSkillsDisplayed"] = ccparams.classSkillsDisplayed
            context_dict["skillLeaderboardDisplayed"] = ccparams.skillLeaderboardDisplayed
            context_dict["studCanChangeClassSkillsVis"] = ccparams.studCanChangeClassSkillsVis
            context_dict["numStudentBestSkillsDisplayed"] = ccparams.numStudentBestSkillsDisplayed

            # Virtual Currency
            context_dict["virtualCurrencyUsed"] = ccparams.virtualCurrencyUsed
            context_dict["virtualCurrencyAdded"] = ccparams.virtualCurrencyAdded
            
            context_dict["classFundEnabled"] = ccparams.classFundEnabled
            context_dict["classFund"] = currentCourse.Donations 
            # Displaying the menu items of content unlocking and debug system variables
            context_dict['contentUnlockingDisplayed'] = ccparams.contentUnlockingDisplayed
            context_dict['debugSystemVariablesDisplayed'] = ccparams.debugSystemVariablesDisplayed

            # Avatars
            context_dict["avatarUsed"] = ccparams.avatarUsed
            context_dict["useCustomAvatar"] = ccparams.useCustomAvatar        
                
            # Student Settings
            
            context_dict["studCanChangeclassAverageVis"] = ccparams.studCanChangeclassAverageVis

            # Challenge Difficulty
            context_dict["thresholdToLevelMedium"] = ccparams.thresholdToLevelMedium
            context_dict["thresholdToLevelDifficulty"] = ccparams.thresholdToLevelDifficulty

            # Duels & callout
            context_dict["classmatesChallenges"] = ccparams.classmatesChallenges
            context_dict["vc_callout"] = ccparams.vcCallout
            context_dict["vc_duel"] = ccparams.vcDuel
            context_dict["betVC"] = ccparams.betVC
            context_dict["vc_duel_participants"] = ccparams.vcDuelParticipants
            context_dict["vc_duel_max_bet"] = ccparams.vcDuelMaxBet
            context_dict["calloutAfterWarmup"] = ccparams.calloutAfterWarmup
            context_dict["minimumCreditPercent"] = ccparams.minimumCreditPercentage

            

            # Goals
            context_dict['goalsUsed'] = ccparams.goalsUsed
            context_dict['studCanChangeGoal'] = ccparams.studCanChangeGoal

            #Player-Types (Adaptation)
            context_dict['adaptationUsed'] = ccparams.adaptationUsed
     
            #Virtual applause
            context_dict['applauseOn'] = ccparams.applauseOn
            

        return render(request, 'Instructors/Preferences.html', context_dict)

def createSCVforInstructorGrant(student, course, vc):
    svc = StudentVirtualCurrency()
    svc.studentID = student
    svc.courseID = course
    svc.objectID = 0
    svc.value = vc
    svc.vcName = "Instructor Grant"
    svc.vcDescription = "All students were issued virtual currency"
    svc.save()
