'''
Created on Oct 28, 2014

@author: Swapna
'''
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Badges.views.badgesDisplayView import BadgesDisplay
from Badges.views.badgesView import BadgesMain

from Badges.views.createBadgeView import CreateBadge
from Badges.views.createVirtualCurrencyRuleView import CreateVcRule
from Badges.views.createVirtualCurrencySpendRuleView import CreateVcSpendRule
from Badges.views.editDeleteBadgeView import EditDeleteBadge
from Badges.views.editVirtualCurrencyRuleView import EditVirtualCurrencyRule
from Badges.views.editVirtualCurrencySpendRuleView import EditVirtualCurrencySpendRule
from Badges.views.saveBadgeView import SaveBadge
from Badges.views.saveVirtualCurrencyRule import SaveVirtualCurrencyRule
from Badges.views.saveVirtualCurrencySpendRule import SaveVirtualCurrencySpendRule
from Badges.views.virtualCurrencyListView import VirtualCurrencyList
from Badges.views.conditionTestView import conditionTestView

admin.autodiscover()

urlpatterns = [    
    url(r'^Badges',BadgesMain, name='BadgesMain'),
    url(r'^CreateBadge',CreateBadge, name='CreateBadge'),
    url(r'^CreateVirtualCurrencySpendRule',CreateVcSpendRule, name='Create Virtual Currency Spend Rule'),
    url(r'^CreateVirtualCurrencyRule',CreateVcRule, name='Create Virtual Currency Rule'),
    url(r'^CourseBadges', BadgesDisplay, name='BadgeDisplay'),
    url(r'^EditDeleteBadge',EditDeleteBadge, name='EditDeleteBadge'),
    url(r'^EditVirtualCurrencyRule',EditVirtualCurrencyRule, name='Edit Virtual Currency Rule'),
    url(r'^EditVirtualCurrencySpendRule',EditVirtualCurrencySpendRule, name='Edit Virtual Currency Spend Rule'),
    url(r'^SaveBadge',SaveBadge, name='SaveBadge'),
    url(r'^SaveVirtualCurrencyRule',SaveVirtualCurrencyRule, name='Save Virtual Currency Rule'),
    url(r'^SaveVirtualCurrencySpendRule',SaveVirtualCurrencySpendRule, name='Save Virtual Currency Spend Rule'),
    url(r'^InstructorVirtualCurrencyList',VirtualCurrencyList, name='Instructor Virtual Currency List'),
    url(r'^ConditionTestView',conditionTestView, name="Condition Test View"),
    
]
