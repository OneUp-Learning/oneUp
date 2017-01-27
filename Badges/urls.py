'''
Created on Oct 28, 2014

@author: Swapna
'''
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Badges.views.badgesView import BadgesMain

from Badges.views.createBadgeView import CreateBadge
from Badges.views.editDeleteBadgeView import EditDeleteBadge
from Badges.views.saveBadgeView import SaveBadge
from Badges.views.badgesDisplayView import BadgesDisplay

admin.autodiscover()

urlpatterns = [    
    url(r'^Badges',BadgesMain, name='BadgesMain'),
    url(r'^CreateBadge',CreateBadge, name='CreateBadge'),
    url(r'^CourseBadges', BadgesDisplay, name='BadgeDisplay'),
    url(r'^EditDeleteBadge',EditDeleteBadge, name='EditDeleteBadge'),
    url(r'^SaveBadge',SaveBadge, name='SaveBadge'),
    
]
