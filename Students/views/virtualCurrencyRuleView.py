'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments
from Badges.enums import Action
from Students.views.utils import studentInitialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def VirtualCurrencyDisplay(request):

    context_dict,currentCourse = studentInitialContextDict(request)
         
    vcEarningRuleID = [] 
    vcEarningRuleName = []
    vcEarningRuleDescription = []
    vcEarningRuleAmount = []
    vcSpendingRuleID = [] 
    vcSpendingRuleName = []
    vcSpendingRuleDescription = []
    vcSpendingRuleAmount = []
    countEarningRules = 0
    countSpendingRules = 0
            
    #Displaying the list of rules from database
    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse)
    for rule in vcRules:
        if rule.ruleID.actionID == Action.increaseVirtualCurrency:
            vcEarningRuleID.append(rule.vcRuleID)
            vcEarningRuleName.append(rule.vcRuleName)
            vcEarningRuleDescription.append(rule.vcRuleDescription)
            value = -9000000000
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                value = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
            vcEarningRuleAmount.append(value)
            countEarningRules = countEarningRules+1        
        else:
            vcSpendingRuleID.append(rule.vcRuleID)
            vcSpendingRuleName.append(rule.vcRuleName)
            vcSpendingRuleDescription.append(rule.vcRuleDescription)
            value = -9000000000
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                value = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
            vcSpendingRuleAmount.append(value)
            countSpendingRules = countSpendingRules+1
             
        # The range part is the index numbers.
    context_dict['vcEarningRuleInfo'] = zip(range(1,countEarningRules+1),vcEarningRuleID,vcEarningRuleName, vcEarningRuleDescription, vcEarningRuleAmount)
    context_dict['vcSpendingRuleInfo'] = zip(range(1,countSpendingRules+1),vcSpendingRuleID,vcSpendingRuleName, vcSpendingRuleDescription, vcSpendingRuleAmount)

    return render(request,'Students/VirtualCurrencyRules.html', context_dict)