'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo, ActionArguments
from Badges.events import register_event
from Badges.enums import Event

from Students.views.utils import studentInitialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def VirtualCurrencyDisplay(request):

    context_dict,currentCourse = studentInitialContextDict(request)
    
    studentId = context_dict['student']
    register_event(Event.visitedVCRulesInfoPage, request, studentId, None)
             
    vcEarningRuleID = [] 
    vcEarningRuleName = []
    vcEarningRuleDescription = []
    vcEarningRuleAmount = []
    vcSpendingRuleID = [] 
    vcSpendingRuleName = []
    vcSpendingRuleDescription = []
    vcSpendingRuleAmount = []
    vcSpendingRuleLimit = []
    countEarningRules = 0
    countSpendingRules = 0
            
    #Displaying the list of rules from database
    #vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse)
    vcRules = VirtualCurrencyCustomRuleInfo.objects.filter(courseID=currentCourse).order_by('vcRulePosition')  # 01/18/18 DD
    for rule in vcRules:
        if rule.vcRuleType:
        #if rule.ruleID.actionID == Action.increaseVirtualCurrency:
        
        # earning rule
            vcEarningRuleID.append(rule.vcRuleID)
            vcEarningRuleName.append(rule.vcRuleName)
            vcEarningRuleDescription.append(rule.vcRuleDescription)
            if rule.vcRuleAmount == -1:   # an automatic rule, take the amount from action arguments
                value = -9000000000
                a_rule = VirtualCurrencyRuleInfo.objects.get(vcRuleID=rule.vcRuleID)
                if (ActionArguments.objects.filter(ruleID=a_rule.ruleID).exists()):
                    value = ActionArguments.objects.get(ruleID=a_rule.ruleID).argumentValue
            else:
                value = rule.vcRuleAmount   # manually handled rule
            vcEarningRuleAmount.append(value)
            countEarningRules = countEarningRules+1  
                  
        else:
            # spending rule
            vcSpendingRuleID.append(rule.vcRuleID)
            vcSpendingRuleName.append(rule.vcRuleName)
            vcSpendingRuleDescription.append(rule.vcRuleDescription)
            if rule.vcRuleAmount == -1:   # an automatic rule, take the amount from action arguments          
                value = -9000000000
                a_rule = VirtualCurrencyRuleInfo.objects.get(vcRuleID=rule.vcRuleID)
                if (ActionArguments.objects.filter(ruleID=a_rule.ruleID).exists()):
                    value = ActionArguments.objects.get(ruleID=a_rule.ruleID).argumentValue
            else:
                value = rule.vcRuleAmount   # manually handled rule
            vcSpendingRuleAmount.append(value)
            vcSpendingRuleLimit.append(rule.vcRuleLimit)
            countSpendingRules = countSpendingRules+1
             
        # The range part is the index numbers.
    context_dict['vcEarningRuleInfo'] = zip(range(1,countEarningRules+1),vcEarningRuleID,vcEarningRuleName, vcEarningRuleDescription, vcEarningRuleAmount)
    context_dict['vcSpendingRuleInfo'] = zip(range(1,countSpendingRules+1),vcSpendingRuleID,vcSpendingRuleName, vcSpendingRuleDescription, vcSpendingRuleAmount, vcSpendingRuleLimit)

    return render(request,'Students/VirtualCurrencyRules.html', context_dict)