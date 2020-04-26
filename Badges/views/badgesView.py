'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Badges.models import Badges, BadgesInfo
from Instructors.views.utils import initialContextDict


@login_required
def BadgesMain(request):
 
    context_dict,current_course = initialContextDict(request)
        
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
    badgePosition = []
    #Displaying the list of challenges from database
    badges = Badges.objects.filter(courseID=current_course).order_by("badgePosition")
    context_dict['numBadges'] = len(badges)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
        badgePosition.append(badge.badgePosition)
        
    
    manualBadgeId = [] 
    manualBadgeName = []
    manualBadgeImage = []
    manualBadgeDescription = []
    manualBadgePosition = []
    #Displaying the list of manual badges from database
    manualBadges = BadgesInfo.objects.filter(courseID=current_course).order_by("badgePosition")
    context_dict['numBadgesMan'] = len(manualBadges) - len(badges)
    for manualBadge in manualBadges:
        if(manualBadge.manual == True):
            manualBadgeId.append(manualBadge.badgeID)
            manualBadgeName.append(manualBadge.badgeName)
            manualBadgeImage.append(manualBadge.badgeImage)
            manualBadgePosition.append(manualBadge.badgePosition)
            manualBadgeDescription.append(manualBadge.badgeDescription)  
                    
        # The range part is the index numbers.
    context_dict['badgesInfo'] = list(zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription, badgePosition))
    context_dict['manualBadgesInfo'] = list(zip(range(1,manualBadges.count()+1),manualBadgeId, manualBadgeName,manualBadgeImage, manualBadgeDescription, manualBadgePosition))

    return render(request,'Badges/Badges.html', context_dict)

@login_required
def reorderBadges(request):
    context_dict,current_course = initialContextDict(request)

    badges = Badges.objects.filter(courseID=current_course).order_by("badgePosition")
    for badge in badges:
        if str(badge.badgeID) in request.POST: 
            badge.badgePosition = request.POST[str(badge.badgeID)]
            badge.save()
        
    manualBadges = BadgesInfo.objects.filter(courseID=current_course).order_by("badgePosition")
    for badge in manualBadges:
        if str(badge.badgeID) in request.POST: 
            badge.badgePosition = request.POST[str(badge.badgeID)]
            badge.save()
    
    return BadgesMain(request)
