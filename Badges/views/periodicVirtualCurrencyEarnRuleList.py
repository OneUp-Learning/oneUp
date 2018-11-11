'''
Created on Nov 9, 2017

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyPeriodicRule
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def periodicVirtualCurrencyEarnRuleList(request):
 
    context_dict, currentCourse = initialContextDict(request)
    
    vcRuleID = [] 
    vcRuleName = []
    vcAmount = []
    vcDescription = []
    vcRules = VirtualCurrencyPeriodicRule.objects.filter(courseID=currentCourse)
    
    for rule in vcRules:
        # Rules that are considered 'Earning' have vcRuleType as True
        vcRuleID.append(rule.vcRuleID)
        vcRuleName.append(rule.vcRuleName)
        vcAmount.append(rule.vcRuleAmount)
        vcDescription.append(rule.vcRuleDescription)
            
    context_dict['vcRuleInfo'] = zip(range(1,len(vcRuleID)+1),vcRuleID,vcRuleName,vcAmount, vcDescription)
    print("Done")
    return render(request,'Badges/PeriodicVirtualCurrencyEarnRuleList.html', context_dict)