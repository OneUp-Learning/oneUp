'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.template import RequestContext
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Skills, Courses, CoursesSkills, Topics, CoursesTopics
from Badges.models import CourseConfigParams
from Students.models import StudentConfigParams

@login_required
def preferencesView(request):

   
    context_dict = { }  
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected' 
    
    if request.POST:
        
        # There is an existing topic, edit it
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
        ccparams.leaderboardUsed = "leaderboardUsed" in request.POST
        if ccparams.leaderboardUsed == True:    
            ccparams.studCanChangeLeaderboardVis = "studCanChangeLeaderboardVis" in request.POST
            ccparams.numStudentsDisplayed = request.POST.get('numStudentsDisplayed')
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
        ccparams.avatarUsed = "avatarUsed" in request.POST
        ccparams.classAverageUsed = "classAverageUsed" in request.POST
        ccparams.studCanChangeclassAverageVis = "studCanChangeclassAverageVis" in request.POST
#         ccparams.courseStartDate = request.POST.get('courseStartDate')
#         ccparams.courseEndDate= request.POST.get('courseEndDate') 
        ccparams.leaderboardUpdateFreq = request.POST.get('leaderboardUpdateFreq')
#         print("Before Save in POST :" ,ccparams.numStudentsDisplayed)
        ccparams.xpWeightSP = request.POST.get('xpWeightSP')
        ccparams.xpWeightSChallenge = request.POST.get('xpWeightSChallenge')
        ccparams.xpWeightSChallenge = request.POST.get('xpWeightSChallenge')
        ccparams.xpWeightAPoints = request.POST.get('xpWeightAPoints')
        ccparams.thresholdToLevelMedium = request.POST.get('thresholdToLevelMedium')
        ccparams.thresholdToLevelDifficulty = request.POST.get('thresholdToLevelDifficulty')
        ccparams.save()
#         print("After Save in POST :" ,ccparams.numStudentsDisplayed)
#         return render(request,'Instructors/InstructorCourseHome.html', context_dict)
        return redirect('/oneUp/instructors/instructorCourseHome',"","")
                
    #################################
    #  get request
    else:
        
        ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
            
        if len(ccparamsList) > 0:
            ccparams = ccparamsList[0]   
            context_dict['ccpID'] = ccparams.ccpID
            context_dict["badgesUsed"]=ccparams.badgesUsed
            context_dict["numBadgesDisplayed"]=ccparams.numBadgesDisplayed
            context_dict["studCanChangeBadgeVis"]=ccparams.studCanChangeBadgeVis
            context_dict["levelingUsed"]=ccparams.levelingUsed
            context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
            context_dict["studCanChangeLeaderboardVis"]=ccparams.studCanChangeLeaderboardVis
            context_dict["numStudentsDisplayed"]=ccparams.numStudentsDisplayed
#             print(context_dict["numStudentsDisplayed"])
            context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
            context_dict["studCanChangeClassSkillsVis"]=ccparams.studCanChangeClassSkillsVis
            context_dict["numStudentBestSkillsDisplayed"]=ccparams.numStudentBestSkillsDisplayed
            context_dict["virtualCurrencyUsed"]=ccparams.virtualCurrencyUsed
            context_dict["avatarUsed"]=ccparams.avatarUsed
            context_dict["classAverageUsed"]=ccparams.classAverageUsed
            context_dict["studCanChangeclassAverageVis"]=ccparams.studCanChangeclassAverageVis
            context_dict["courseStartDate"]=ccparams.courseStartDate
            context_dict["courseEndDate"]=ccparams.courseEndDate
            context_dict["leaderboardUpdateFreq"]=ccparams.leaderboardUpdateFreq
            context_dict["xpWeightSP"]=ccparams.xpWeightSP
            context_dict["xpWeightSChallenge"]=ccparams.xpWeightSChallenge
            context_dict["xpWeightWChallenge"]=ccparams.xpWeightWChallenge
            context_dict["xpWeightAPoints"]=ccparams.xpWeightAPoints
            context_dict["thresholdToLevelMedium"]=ccparams.thresholdToLevelMedium
            context_dict["thresholdToLevelDifficulty"]=ccparams.thresholdToLevelDifficulty
#             context_dict["latestBadgesUsed"]=ccparams.latestBadgesUsed
#             context_dict["levellingUsed"]=ccparams.levellingUsed
#             context_dict["leaderBoardUsed"]=ccparams.leaderBoardUsed
#             context_dict["virtualCurrencyUsed"]=ccparams.virtualCurrencyUsed
#             context_dict["avatarUsed"]=ccparams.avatarUsed
#             context_dict["classAverageUsed"]=ccparams.classAverageUsed
#             context_dict["numStudentToppersUsed"]=int(ccparams.numStudentToppersUsed)
#             context_dict["numStudentBestSkillsUsed"]=int(ccparams.numStudentBestSkillsUsed)
#             print (ccparams.numStudentToppersUsed)
#             print (ccparams.numStudentBestSkillsUsed)
    #    else:
#             print(context_dict)    
        return render(request,'Instructors/Preferences.html', context_dict)
#     print (context_dict)
#     context_dict['ccpID'] = ccparams.ccpID
#     context_dict["badgesUsed"]=ccparams.badgesUsed
#     print (context_dict)
    


