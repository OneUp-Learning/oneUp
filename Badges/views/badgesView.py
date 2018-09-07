'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.shortcuts import render

from Badges.models import Badges, BadgesInfo, PeriodicBadges

from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict

@login_required
def BadgesMain(request):
 
    context_dict,current_course = initialContextDict(request);
        
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
    #Displaying the list of challenges from database
    badges = Badges.objects.filter(courseID=current_course)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
        
    
    manualBadgeId = [] 
    manualBadgeName = []
    manualBadgeImage = []
    manualBadgeDescription = []
    #Displaying the list of manual badges from database
    manualBadges = BadgesInfo.objects.filter(courseID=current_course)
    for manualBadge in manualBadges:
        if(manualBadge.manual == True):
            manualBadgeId.append(manualBadge.badgeID)
            manualBadgeName.append(manualBadge.badgeName)
            manualBadgeImage.append(manualBadge.badgeImage)
            manualBadgeDescription.append(manualBadge.badgeDescription)  
            
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
              
                    
        # The range part is the index numbers.
    context_dict['badgesInfo'] = zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription)
    
    context_dict['manualBadgesInfo'] = zip(range(1,manualBadges.count()+1),manualBadgeId, manualBadgeName,manualBadgeImage, manualBadgeDescription)
    
    context_dict['periodicBadgesInfo'] = zip(range(1,periodicBadges.count()+1),periodicBadgeId, periodicBadgeName,periodicBadgeImage, periodicBadgeDescription)
    return render(request,'Badges/Badges.html', context_dict)