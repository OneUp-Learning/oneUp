'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.shortcuts import render

from Badges.models import Badges, BadgesInfo

from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict

@login_required
def BadgesMain(request):
 
    context_dict,current_course = initialContextDict(request);
        
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
    badgePostion = []
    #Displaying the list of challenges from database
    badges = Badges.objects.filter(courseID=current_course).order_by("badgePostion")
    context_dict['numBadges'] = len(badges)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
        badgePostion.append(badge.badgePostion)
        
    
    manualBadgeId = [] 
    manualBadgeName = []
    manualBadgeImage = []
    manualBadgeDescription = []
    manualBadgePostion = []
    #Displaying the list of manual badges from database
    manualBadges = BadgesInfo.objects.filter(courseID=current_course).order_by("badgePostion")
    context_dict['numBadgesMan'] = len(manualBadges) - len(badges)
    for manualBadge in manualBadges:
        if(manualBadge.manual == True):
            manualBadgeId.append(manualBadge.badgeID)
            manualBadgeName.append(manualBadge.badgeName)
            manualBadgeImage.append(manualBadge.badgeImage)
            manualBadgeDescription.append(manualBadge.badgeDescription)    
            manualBadgePostion.append(manualBadge.badgePostion)
                    
        # The range part is the index numbers.
    context_dict['badgesInfo'] = zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription, badgePostion)
    
    context_dict['manualBadgesInfo'] = zip(range(1,manualBadges.count()+1),manualBadgeId, manualBadgeName,manualBadgeImage, manualBadgeDescription, manualBadgePostion)

    return render(request,'Badges/Badges.html', context_dict)

@login_required
def reorderBadges(request):
    context_dict,current_course = initialContextDict(request);

    badges = Badges.objects.filter(courseID=current_course).order_by("badgePostion")
    for badge in badges:
        if str(badge.badgeID) in request.POST: 
            badge.badgePostion = request.POST[str(badge.badgeID)]
            badge.save()
        
    manualBadges = BadgesInfo.objects.filter(courseID=current_course).order_by("badgePostion")
    for badge in manualBadges:
        if str(badge.badgeID) in request.POST: 
            badge.badgePostion = request.POST[str(badge.badgeID)]
            badge.save()
    
    return BadgesMain(request)