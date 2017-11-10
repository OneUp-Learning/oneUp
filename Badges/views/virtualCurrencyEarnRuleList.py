'''
Created on Nov 9, 2017

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments, Conditions, FloatConstants, StringConstants
from Badges.enums import OperandTypes
from Badges.systemVariables import SystemVariable
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def virtualCurrencyEarnRuleList(request):
 
    context_dict, currentCourse = initialContextDict(request)
        
    def operandToString(operandType,value):
        if (operandType == OperandTypes.immediateInteger):
            return str(value)
        elif (operandType == OperandTypes.condition):
            return str(Conditions.objects.get(pk=value))
        elif (operandType == OperandTypes.floatConstant):
            return str(FloatConstants.objects.get(pk=value))
        elif (operandType == OperandTypes.stringConstant):
            return str(StringConstants.objects.get(pk=value))
        elif (operandType == OperandTypes.systemVariable): 
            if value in SystemVariable.systemVariables:
                if 'displayName' in SystemVariable.systemVariables[value]:
                    return SystemVariable.systemVariables[value]['displayName']
    vcRuleID = [] 
    vcRuleName = []
    vcAmount = []
    
    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse)
    
    for rule in vcRules:
        # Rules that are considered 'Earning' have vcRuleType as True
        if rule.vcRuleType == True:
            vcRuleID.append(rule.vcRuleID)
            vcRuleName.append(rule.vcRuleName)
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                vcAmount.append(ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue)
            else:
                vcAmount.append(0)
                    
    context_dict['vcRuleInfo'] = zip(range(1,len(vcRuleID)+1),vcRuleID,vcRuleName,vcAmount)

    return render(request,'Badges/VirtualCurrencyEarnRuleList.html', context_dict)