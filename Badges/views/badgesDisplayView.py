'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import Badges, BadgesInfo
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.enums import Event

from django.contrib.auth.decorators import login_required
from notify.models import NotificationQueryset, Notification


@login_required
def BadgesDisplay(request):
 
    context_dict, currentCourse = studentInitialContextDict(request)
 
    studentId = context_dict['student']
    register_event(Event.visitedBadgesInfoPage, request, studentId, None)
    register_event(Event.visitedLeaderboardPage, request, studentId, None)
           
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
        
    #Displaying the list of challenges from database
    badges = BadgesInfo.objects.filter(courseID=currentCourse)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
             
                    
    # The range part is the index numbers.
    context_dict['badgesInfo'] = zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription)

    return render(request,'Students/CourseBadges.html', context_dict)