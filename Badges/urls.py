'''
Created on Oct 28, 2014

@author: Swapna
'''
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Badges.views.addVirtualCurrencyForStudentWithRuleView import addVirtualCurrencyForStudentWithRuleView
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
from Badges.views.UpdateVirtualCurrencyTransaction import updateVirtualCurrencyTransaction
from Badges.views.virtualCurrencyEarnRuleList import virtualCurrencyEarnRuleList
from Badges.views.virtualCurrencySpendRuleList import virtualCurrencySpendRuleList
from Badges.views.VirtualCurrencyTransactions import virtualCurrencyTransactions
from Badges.views.VirtualCurrencyCompletedTransactions import virtualCurrencyCompletedTransactions
from Badges.views.conditionTestView import conditionTestView

admin.autodiscover()

urlpatterns = [    
    url(r'^AddVirtualCurrency', addVirtualCurrencyForStudentWithRuleView, name='Add Virtual Currency to Students'),
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
    url(r'^VirtualCurrencyEarnRuleList',virtualCurrencyEarnRuleList, name='Instructor Virtual Currency Earn Rule List'),
    url(r'^VirtualCurrencySpendRuleList',virtualCurrencySpendRuleList, name='Instructor Virtual Currency Spend Rule List'),
    url(r'^ConditionTestView',conditionTestView, name="Condition Test View"),
    url(r'^UpdateVirtualCurrencyTransaction',updateVirtualCurrencyTransaction, name="Update Virtual Currency Transaction"),
    url(r'^VirtualCurrencyTransactions',virtualCurrencyTransactions, name="Virtual Currency Transactions"),
    url(r'^VirtualCurrencyCompletedTransactions',virtualCurrencyCompletedTransactions, name="Virtual Currency Completed Transactions"),
    
]
