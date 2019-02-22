'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Badges.models import CourseConfigParams
from Students.models import StudentRegisteredCourses
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck   

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

        ccparams.badgesUsed = "badgesUsed" in request.POST
        if ccparams.badgesUsed == True:    
            ccparams.studCanChangeBadgeVis = "studCanChangeBadgeVis" in request.POST
            ccparams.numBadgesDisplayed = request.POST.get('numBadgesDisplayed')
        else:
            ccparams.studCanChangeBadgeVis =False
            ccparams.numBadgesDisplayed=0
            
        ccparams.levelingUsed = "levelingUsed" in request.POST
            
        ccparams.classmatesChallenges = "classmatesChallenges" in request.POST
        if ccparams.classmatesChallenges:
            ccparams.vcDuel = request.POST.get('vc_duel')
            ccparams.vcCallout = request.POST.get('vc_callout')
            ccparams.vcDuelParticipants = request.POST.get('vc_duel_participants')
        else:
            ccparams.vcDuel = 0
            ccparams.vcCallout = 0
            ccparams.vcDuelParticipants = 0
        ccparams.betVC = "betVC" in request.POST
        
        ccparams.leaderboardUsed = "leaderboardUsed" in request.POST
        if ccparams.leaderboardUsed == True:    
            ccparams.studCanChangeLeaderboardVis = "studCanChangeLeaderboardVis" in request.POST
        else:
            ccparams.studCanChangeLeaderboardVis =False
            ccparams.numStudentsDisplayed = 0
            
        ccparams.classSkillsDisplayed = "classSkillsDisplayed" in request.POST
        if ccparams.classSkillsDisplayed == True:
            ccparams.studCanChangeClassSkillsVis = "studCanChangeClassSkillsVis" in request.POST
            ccparams.numStudentBestSkillsDisplayed = request.POST.get('numStudentBestSkillsDisplayed')
        else:
            ccparams.studCanChangeClassSkillsVis = False
            ccparams.numStudentBestSkillsDisplayed = 0
            
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
        ccparams.save()

        return redirect('/oneUp/instructors/instructorCourseHome',"","")
                
    elif request.method == 'GET':
        
        ccparams = context_dict['ccparams']
            
        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID
            context_dict["badgesUsed"]=ccparams.badgesUsed
            context_dict["numBadgesDisplayed"]=ccparams.numBadgesDisplayed
            context_dict["studCanChangeBadgeVis"]=ccparams.studCanChangeBadgeVis
            context_dict["levelingUsed"]=ccparams.levelingUsed
            context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
            context_dict["studCanChangeLeaderboardVis"]=ccparams.studCanChangeLeaderboardVis
            context_dict["numStudentsDisplayed"]=ccparams.numStudentsDisplayed
            context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
            context_dict["studCanChangeClassSkillsVis"]=ccparams.studCanChangeClassSkillsVis
            context_dict["numStudentBestSkillsDisplayed"]=ccparams.numStudentBestSkillsDisplayed
            context_dict["virtualCurrencyUsed"]=ccparams.virtualCurrencyUsed
            context_dict["virtualCurrencyAdded"]=ccparams.virtualCurrencyAdded
            context_dict["avatarUsed"]=ccparams.avatarUsed
            context_dict["classAverageUsed"]=ccparams.classAverageUsed
            context_dict["studCanChangeclassAverageVis"]=ccparams.studCanChangeclassAverageVis
            context_dict["leaderboardUpdateFreq"]=ccparams.leaderboardUpdateFreq
            context_dict["thresholdToLevelMedium"]=ccparams.thresholdToLevelMedium
            context_dict["thresholdToLevelDifficulty"]=ccparams.thresholdToLevelDifficulty
            context_dict["classmatesChallenges"]=ccparams.classmatesChallenges
            context_dict["vc_callout"] = ccparams.vcCallout
            context_dict["vc_duel"] = ccparams.vcDuel
            context_dict["betVC"] = ccparams.betVC
            context_dict["vc_duel_participants"] = ccparams.vcDuelParticipants
            context_dict["streaksUsed"] = ccparams.streaksUsed
            
 
        return render(request,'Instructors/Preferences.html', context_dict)
    


