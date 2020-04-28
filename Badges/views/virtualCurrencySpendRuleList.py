'''
Created on Nov 9, 2017

@author: Austin Hodge
'''

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Badges.enums import OperandTypes
from Badges.models import (ActionArguments, Conditions, FloatConstants,
                           StringConstants, VirtualCurrencyCustomRuleInfo,
                           VirtualCurrencyRuleInfo)
from Badges.systemVariables import SystemVariable
from Instructors.constants import unlimited_constant
from Instructors.views.utils import initialContextDict


@login_required
def virtualCurrencySpendRuleList(request):
 
    context_dict, currentCourse = initialContextDict(request)

    vcsRuleID = [] 
    vcsRuleName = []
    vcsAmount = [] 
    vcsLimit = []
    position = []
    
    vcRules = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=False, courseID=currentCourse).order_by('vcRulePosition')
    
    for rule in vcRules:
        vcsRuleID.append(rule.vcRuleID)
        vcsRuleName.append(rule.vcRuleName)
        position.append(rule.vcRulePosition)
        vcsAmount.append(rule.vcRuleAmount or 0)
        vcsLimit.append(rule.vcRuleLimit if (not rule.vcRuleLimit == unlimited_constant) and (not rule.vcRuleLimit == 0) else "Unlimited")
                    
    context_dict['vcsRuleInfo'] = list(zip(range(1,len(vcsRuleID)+1),vcsRuleID,vcsRuleName,vcsAmount, vcsLimit, position))

    return render(request,'Badges/VirtualCurrencySpendRuleList.html', context_dict)

@login_required
def reorderVcSpendRuleList(request):
    context_dict,currentCourse = initialContextDict(request);

    vcRules = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=False, courseID=currentCourse).order_by('vcRulePosition')
    for rule in vcRules:
        if str(rule.vcRuleID) in request.POST:
            rule.vcRulePosition = request.POST[str(rule.vcRuleID)]
            rule.save()
    
    return virtualCurrencySpendRuleList(request)
