'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Badges.models import CourseConfigParams
from Students.models import StudentConfigParams
from Students.views.utils import studentInitialContextDict


@login_required
def preferencesView(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    if 'currentCourseID' in request.session:

        c_ccparams = CourseConfigParams.objects.filter(courseID=currentCourse)

        if len(c_ccparams) > 0:
            ccparams = c_ccparams[0]
            context_dict['studCanChangeBadgeVis'] = ccparams.studCanChangeBadgeVis
            context_dict['studCanChangeLeaderboardVis'] = ccparams.studCanChangeLeaderboardVis
            context_dict['studCanChangeClassSkillsVis'] = ccparams.studCanChangeClassSkillsVis
            context_dict['studCanChangeclassAverageVis'] = ccparams.studCanChangeclassAverageVis
            context_dict["classmatesChallenges"] = ccparams.classmatesChallenges
            context_dict["studCanChangeGoal"] = ccparams.studCanChangeGoal

        student = context_dict['student']
    if request.POST:
        
        if request.POST['scpID']:
            scparams = StudentConfigParams.objects.get(
                pk=int(request.POST['scpID']))

        else:
            scparams = StudentConfigParams.objects.get(
                courseID=currentCourse, studentID=student)
        student.displayDarkMode = "displayDarkMode" in request.POST
        student.save()

        if ccparams.studCanChangeBadgeVis:
            scparams.displayBadges = "displayBadges" in request.POST

        if ccparams.studCanChangeLeaderboardVis:
            scparams.displayLeaderBoard = "displayLeaderBoard" in request.POST

        if ccparams.studCanChangeClassSkillsVis:
            scparams.displayClassSkills = "displayClassSkills" in request.POST

        if ccparams.studCanChangeclassAverageVis:
            scparams.displayClassAverage = "displayClassAverage" in request.POST

        if ccparams.classmatesChallenges:
            scparams.participateInDuel = "participateInDuel" in request.POST
            scparams.participateInCallout = "participateInCallout" in request.POST

        if ccparams.studCanChangeGoal:
            scparams.displayGoal = "displayGoal" in request.POST

        # scparams.displayClassAverage = "displayClassAverage" in request.POST
        scparams.displayClassRanking = "displayClassRanking" in request.POST
        scparams.save()
        print(scparams, scparams.courseID, scparams.studentID, scparams.displayBadges,
              scparams.displayLeaderBoard, scparams.displayClassSkills)
        return redirect('/oneUp/students/StudentCourseHome', "", "")

    #################################
    #  get request
    #  For the fields that are not visbile because the instructor did not choose to be used for the course. you can pass false so null exceptions are not created
    else:
        ccparams = CourseConfigParams.objects.filter(courseID=currentCourse)
    
        scparamsList = StudentConfigParams.objects.filter(
            courseID=currentCourse, studentID=student)
            
        if (len(scparamsList) > 0):
            scparams = scparamsList[0]
            context_dict['scpID'] = scparams.scpID
            context_dict["displayBadges"] = scparams.displayBadges
            context_dict["displayLeaderBoard"] = scparams.displayLeaderBoard
            context_dict["displayClassAverage"] = scparams.displayClassAverage
            context_dict["displayClassSkills"] = scparams.displayClassSkills
            context_dict["displayClassRanking"] = scparams.displayClassRanking
            context_dict["participateInDuel"] = scparams.participateInDuel
            context_dict["participateInCallout"] = scparams.participateInCallout
            context_dict["displayGoal"]=scparams.displayGoal

        return render(request, 'Students/Preferences.html', context_dict)
