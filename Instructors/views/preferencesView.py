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
            ccparams = CourseConfigParams.objects.get(pk=int(request.POST['ccpID']))
        else:
            # Create new Config Parameters
            ccparams = CourseConfigParams()
            ccparams.courseID = currentCourse
        ccparams.badgesUsed = "badgesUsed" in request.POST
        ccparams.studCanChangeBadgeVis = "studCanChangeBadgeVis" in request.POST
        ccparams.levelingUsed = "levelingUsed" in request.POST
        ccparams.leaderboardUsed = "leaderboardUsed" in request.POST
        ccparams.studCanChangeLeaderboardVis  = "studCanChangeLeaderboardVis" in request.POST
        ccparams.numStudentToppersDisplayed = request.POST.get('numStudentToppersDisplayed')
        ccparams.classSkillsDisplayed = "classSkillsDisplayed" in request.POST
        ccparams.studCanChangeClassSkillsVis = "studCanChangeClassSkillsVis" in request.POST
        ccparams.numStudentBestSkillsDisplayed = request.POST.get('numStudentBestSkillsDisplayed')
        ccparams.classRankingDisplayed = "classRankingDisplayed" in request.POST
        ccparams.studCanChangeClassRankingVis  = "studCanChangeClassRankingVis" in request.POST
        ccparams.virtualCurrencyUsed  = "virtualCurrencyUsed" in request.POST
        ccparams.avatarUsed = "avatarUsed" in request.POST
        ccparams.classAverageUsed = "classAverageUsed" in request.POST
        ccparams.studCanChangeclassAverageVis = "studCanChangeclassAverageVis" in request.POST
#         ccparams.courseStartDate = request.POST.get('courseStartDate')
#         ccparams.courseEndDate= request.POST.get('courseEndDate') 
        ccparams.leaderBoardUpdateFreq = request.POST.get('leaderBoardUpdateFreq')
        ccparams.leaderBoardUpdateFreq= request.POST.get('leaderBoardUpdateFreq')
#         print("Before Save in POST :" ,ccparams.numStudentToppersDisplayed)
        ccparams.save()
#         print("After Save in POST :" ,ccparams.numStudentToppersDisplayed)
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
            context_dict["studCanChangeBadgeVis"]=ccparams.studCanChangeBadgeVis
            context_dict["levelingUsed"]=ccparams.levelingUsed
            context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
            context_dict["studCanChangeLeaderboardVis"]=ccparams.studCanChangeLeaderboardVis
            context_dict["numStudentToppersDisplayed"]=ccparams.numStudentToppersDisplayed
            print(context_dict["numStudentToppersDisplayed"])
            context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
            context_dict["studCanChangeClassSkillsVis"]=ccparams.studCanChangeClassSkillsVis
            context_dict["numStudentBestSkillsDisplayed"]=ccparams.numStudentBestSkillsDisplayed
            context_dict["classRankingDisplayed "]=ccparams.classRankingDisplayed
            context_dict["studCanChangeClassRankingVis"]=ccparams.studCanChangeClassRankingVis
            context_dict["virtualCurrencyUsed"]=ccparams.virtualCurrencyUsed
            context_dict["avatarUsed"]=ccparams.avatarUsed
            context_dict["classAverageUsed"]=ccparams.classAverageUsed
            context_dict["studCanChangeclassAverageVis"]=ccparams.studCanChangeclassAverageVis
            context_dict["courseStartDate"]=ccparams.courseStartDate
            context_dict["courseEndDate"]=ccparams.courseEndDate
            context_dict["leaderBoardUpdateFreq"]=ccparams.leaderBoardUpdateFreq
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
            print(context_dict)    
        return render(request,'Instructors/Preferences.html', context_dict)
    print (context_dict)
#     context_dict['ccpID'] = ccparams.ccpID
#     context_dict["badgesUsed"]=ccparams.badgesUsed
#     print (context_dict)
    

