'''
Created on Oct 28, 2014

@author: Swapna
'''
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Badges.views.addVirtualCurrencyForStudentWithRuleView import addVirtualCurrencyForStudentWithRuleView
from Badges.views.badgesDisplayView import BadgesDisplay
from Badges.views.badgesView import BadgesMain, reorderBadges

from Badges.views.createVirtualCurrencyRuleView import CreateVcRule
from Badges.views.editDeleteBadgeView import EditDeleteBadge
from Badges.views.editVirtualCurrencyRuleView import EditVirtualCurrencyRule
from Badges.views.selectVirtualCurrencySpendRuleView import SelectVirtualCurrencySpendRule
from Badges.views.saveBadgeView import SaveBadge
from Badges.views.saveVirtualCurrencyRule import SaveVirtualCurrencyRule
from Badges.views.saveVirtualCurrencySpendRule import SaveVirtualCurrencySpendRule
from Badges.views.UpdateVirtualCurrencyTransaction import updateVirtualCurrencyTransaction
from Badges.views.virtualCurrencyEarnRuleList import virtualCurrencyEarnRuleList, reorderVirtualCurrencyEarnRules
from Badges.views.virtualCurrencySpendRuleList import virtualCurrencySpendRuleList, reorderVcSpendRuleList
from Badges.views.VirtualCurrencyTransactions import virtualCurrencyTransactions
from Badges.views.VirtualCurrencyCompletedTransactions import virtualCurrencyCompletedTransactions
from Badges.views.conditionTestView import conditionTestView
from Badges.views.addBadgeManuallyView import addBadgeManuallyView
from Badges.views.timeBasedBadgeView import timeBasedBadgeView
from Badges.views.timeBasedVirtualCurrencyView import timeBasedVirtualCurrencyView
from Badges.views.periodicBadgeView import PeriodicBadgeView
from Badges.views.progressiveUnlocking import ProgressiveUnlockingRules, getObjs
from Badges.views.periodicVirtualCurrencyEarnRuleList import periodicVirtualCurrencyEarnRuleList
admin.autodiscover()

urlpatterns = [    
    url(r'^AddVirtualCurrency', addVirtualCurrencyForStudentWithRuleView, name='Add Virtual Currency to Students'),
    url(r'^Badges',BadgesMain, name='BadgesMain'),
    url(r'^CreateVirtualCurrencyRule',CreateVcRule, name='Create Virtual Currency Rule'),
    url(r'^CourseBadges', BadgesDisplay, name='BadgeDisplay'),
    url(r'^EditDeleteBadge',EditDeleteBadge, name='EditDeleteBadge'),
    url(r'^EditVirtualCurrencyRule',EditVirtualCurrencyRule, name='Edit Virtual Currency Rule'),
    url(r'^reorderBadges', reorderBadges, name='reorderBadges'),
    url(r'^reorderVcSpendRuleList', reorderVcSpendRuleList, name='reorderVcSpendRuleList'),
    url(r'^reorderVirtualCurrencyEarnRules', reorderVirtualCurrencyEarnRules, name='reorderVirtualCurrencyEarnRules'),
    url(r'^SelectVirtualCurrencySpendRule',SelectVirtualCurrencySpendRule, name='Edit Virtual Currency Spend Rule'),
    url(r'^SaveBadge',SaveBadge, name='SaveBadge'),
    url(r'^SaveVirtualCurrencyRule',SaveVirtualCurrencyRule, name='Save Virtual Currency Rule'),
    url(r'^SaveVirtualCurrencySpendRule',SaveVirtualCurrencySpendRule, name='Save Virtual Currency Spend Rule'),
    url(r'^VirtualCurrencyEarnRuleList',virtualCurrencyEarnRuleList, name='Instructor Virtual Currency Earn Rule List'),
    url(r'^VirtualCurrencySpendRuleList',virtualCurrencySpendRuleList, name='Instructor Virtual Currency Spend Rule List'),
    url(r'^ConditionTestView',conditionTestView, name="Condition Test View"),
    url(r'^UpdateVirtualCurrencyTransaction',updateVirtualCurrencyTransaction, name="Update Virtual Currency Transaction"),
    url(r'^VirtualCurrencyTransactions',virtualCurrencyTransactions, name="Virtual Currency Transactions"),
    url(r'^VirtualCurrencyCompletedTransactions',virtualCurrencyCompletedTransactions, name="Virtual Currency Completed Transactions"),
    url(r'^AddBadgeManually',addBadgeManuallyView, name="Add Badge Manually"),
    url(r'^TimeBasedBadge',timeBasedBadgeView, name="Periodic Badges"),
    url(r'^TimeBasedVirtualCurrency',timeBasedVirtualCurrencyView, name="Periodic Virtual Currency"),
    url(r'^PeriodicBadges',PeriodicBadgeView, name="Periodic Badges"),
    url(r'^PeriodicVirtualCurrencyEarnRuleList',periodicVirtualCurrencyEarnRuleList, name="Periodic Virtual Currency Earn Rule List"),
    url(r'^ProgressiveUnlocking',ProgressiveUnlockingRules, name="Progressive Unlocking Rules"),
    url(r'^getObjsForPunlocking',getObjs, name="Progressive Unlocking Obj getter"),
]
