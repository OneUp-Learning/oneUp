'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils import timezone

from Badges.models import CourseConfigParams
from Badges.systemVariables import logger
from Instructors.views.utils import initialContextDict, str_datetime_to_local
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def courseConfigurationView(request):

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
            
        ccparams.chatUsed = "chatUsed" in request.POST
        ccparams.seriousChallengesGrouped = "seriousChallengesGrouped" in request.POST
        ccparams.gamificationUsed = "gamificationUsed" in request.POST   
        ccparams.courseAvailable = "courseAvailable" in request.POST
        ccparams.warmupsUsed = "warmupsUsed" in request.POST
        ccparams.seriousChallengesUsed = "seriousUsed" in request.POST
        ccparams.gradebookUsed = "gradebookUsed" in request.POST
        ccparams.activitiesUsed = "activitiesUsed" in request.POST
        ccparams.streaksUsed = 'attendanceUsed' in request.POST
        ccparams.skillsUsed = "skillsUsed" in request.POST
        ccparams.announcementsUsed = "announcementsUsed" in request.POST

        logger.debug(request.POST['courseStartDate'])

        if 'courseStartDate' in request.POST and request.POST['courseStartDate'] != "":
            ccparams.courseStartDate = str_datetime_to_local(request.POST['courseStartDate'], to_format="%B %d, %Y")
            ccparams.hasCourseStartDate = True
        else:
            ccparams.hasCourseStartDate = False
            

        if 'courseEndDate' in request.POST and request.POST['courseEndDate'] != "":
            ccparams.courseEndDate = str_datetime_to_local(request.POST['courseEndDate'], to_format="%B %d, %Y")
            ccparams.hasCourseEndDate = True
        else:
             ccparams.hasCourseEndDate = False

        
        ccparams.save()
        print(ccparams.announcementsUsed,"%%%%%%%%%%")
        return redirect('/oneUp/instructors/instructorCourseHome')
                
    elif request.method == 'GET':
        ccparams = context_dict['ccparams']
        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID
            context_dict['gamificationUsed'] = ccparams.gamificationUsed
            context_dict['chatUsed'] = ccparams.chatUsed
            context_dict['seriousChallengesGrouped'] = ccparams.seriousChallengesGrouped
            context_dict['courseAvailable'] = ccparams.courseAvailable
            
            context_dict['warmupsUsed'] = ccparams.warmupsUsed
            context_dict['seriousUsed'] = ccparams.seriousChallengesUsed
            context_dict['gradebookUsed'] = ccparams.gradebookUsed
            context_dict['attendanceUsed'] = ccparams.streaksUsed
            context_dict['skillsUsed'] = ccparams.skillsUsed
            context_dict['announcementsUsed'] = ccparams.announcementsUsed
            context_dict['activitiesUsed'] = ccparams.activitiesUsed

            if ccparams.hasCourseStartDate:
                context_dict["courseStartDate"]=ccparams.courseStartDate.strftime("%B %d, %Y")
            else:
                context_dict["courseStartDate"]=""

            if ccparams.hasCourseEndDate:
                context_dict["courseEndDate"]=ccparams.courseEndDate.strftime("%B %d, %Y")
            else:
                context_dict["courseEndDate"]=""
 
        return render(request,'Instructors/CourseConfiguration.html', context_dict)
