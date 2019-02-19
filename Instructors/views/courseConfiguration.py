'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required,user_passes_test
from Badges.models import CourseConfigParams
from Instructors.views.utils import initialContextDict, utcDate
from Instructors.constants import default_time_str
from Badges.systemVariables import logger
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
            
        ccparams.progressBarUsed = "progressBarUsed" in request.POST
        ccparams.chatUsed = "chatUsed" in request.POST
        ccparams.seriousChallengesGrouped = "seriousChallengesGrouped" in request.POST
        ccparams.gamificationUsed = "gamificationUsed" in request.POST   
        ccparams.courseAvailable = "courseAvailable" in request.POST
        logger.debug(request.POST['courseStartDate'])
        if('courseStartDate' in request.POST and request.POST['courseStartDate'] == ""):
            ccparams.courseStartDate = utcDate()
        else:
            ccparams.courseStartDate = utcDate(request.POST['courseStartDate'], "%B %d, %Y")

        if('courseEndDate' in request.POST and request.POST['courseEndDate'] == ""):
            ccparams.courseEndDate = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
             ccparams.courseEndDate = utcDate(request.POST['courseEndDate'], "%B %d, %Y")

        
        ccparams.save()

        return redirect('/oneUp/instructors/instructorCourseHome')
                
    elif request.method == 'GET':
        ccparams = context_dict['ccparams']
        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID
            context_dict['gamificationUsed'] = ccparams.gamificationUsed
            context_dict['progressBarUsed'] = ccparams.progressBarUsed
            context_dict['chatUsed'] = ccparams.chatUsed
            context_dict['seriousChallengesGrouped'] = ccparams.seriousChallengesGrouped
            context_dict['courseAvailable'] = ccparams.courseAvailable
           
            defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
            if(ccparams.courseStartDate.year < defaultTime.year):
                context_dict["courseStartDate"]=ccparams.courseStartDate.strftime("%B %d, %Y")
            else:
                context_dict["courseStartDate"]=""
            if(ccparams.courseEndDate.year < defaultTime.year):
                context_dict["courseEndDate"]=ccparams.courseEndDate.strftime("%B %d, %Y")
            else:
                context_dict["courseEndDate"]=""
 
        return render(request,'Instructors/CourseConfiguration.html', context_dict)
    


