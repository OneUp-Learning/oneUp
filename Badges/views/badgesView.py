'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.template import RequestContext
from django.shortcuts import render

from Badges.models import Badges, Courses

from django.contrib.auth.decorators import login_required
from Students.views.utils import studentInitialContextDict
from Badges.models import CourseConfigParams
from Students.models import StudentConfigParams


@login_required
def BadgesMain(request):
 
    context_dict,currentCourse = studentInitialContextDict(request)    
    c_ccparams = CourseConfigParams.objects.filter(courseID=currentCourse)
    
    if len(c_ccparams) > 0:
        ccparams = c_ccparams[0] 
        print('ccparams', ccparams)
        context_dict['studCanChangeBadgeVis']=ccparams.studCanChangeBadgeVis
        context_dict['studCanChangeLeaderboardVis']=ccparams.studCanChangeLeaderboardVis
        context_dict['studCanChangeClassSkillsVis']=ccparams.studCanChangeClassSkillsVis
        context_dict['studCanChangeclassAverageVis']=ccparams.studCanChangeclassAverageVis 
    sID = context_dict['student']
    scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=sID)    
    if len(scparamsList) > 0:
        scparams = scparamsList[0]
        context_dict["displayBadges"]=scparams.displayBadges
        context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
        context_dict["displayClassAverage"]=scparams.displayClassAverage
        context_dict["displayClassSkills"]=scparams.displayClassSkills  

    context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse) 
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
    #Displaying the list of challenges from database
    badges = Badges.objects.filter(courseID=currentCourse)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
                    
        # The range part is the index numbers.
    context_dict['badgesInfo'] = zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription)

    #return render(request,'Badges/ListBadges.html', context_dict)
    return render(request,'Badges/Badges.html', context_dict)