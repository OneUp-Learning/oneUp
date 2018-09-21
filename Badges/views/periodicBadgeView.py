'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.shortcuts import render

from Badges.models import Badges, BadgesInfo, PeriodicBadges

from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict

@login_required
def PeriodicBadgeView(request):
 
    context_dict,current_course = initialContextDict(request);
            
    periodicBadgeId = [] 
    periodicBadgeName = []
    periodicBadgeImage = []
    periodicBadgeDescription = []
    #Displaying the list of manual badges from database
    periodicBadges = PeriodicBadges.objects.filter(courseID=current_course)
    for periodicBadge in periodicBadges:
        if(periodicBadge.isPeriodic == True):
            periodicBadgeId.append(periodicBadge.badgeID)
            periodicBadgeName.append(periodicBadge.badgeName)
            periodicBadgeImage.append(periodicBadge.badgeImage)
            periodicBadgeDescription.append(periodicBadge.badgeDescription)           
              

    
    context_dict['periodicBadgesInfo'] = zip(range(1,periodicBadges.count()+1),periodicBadgeId, periodicBadgeName,periodicBadgeImage, periodicBadgeDescription)
    return render(request,'Badges/PeriodicBadge.html', context_dict)