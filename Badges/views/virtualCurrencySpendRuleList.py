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
def virtualCurrencySpendRuleList(request):
 
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

    vcsRuleID = [] 
    vcsRuleName = []
    vcsAmount = [] 
    position = []
    
    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse).order_by('vcRulePosition')
    
    for rule in vcRules:
        # Rules that are considered 'Spending' have vcRuleType as False
        if rule.vcRuleType == False:
            vcsRuleID.append(rule.vcRuleID)
            vcsRuleName.append(rule.vcRuleName)
            position.append(rule.vcRulePosition)
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                vcsAmount.append(ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue)
            else:
                vcsAmount.append(0)
                    
    context_dict['vcsRuleInfo'] = zip(range(1,len(vcsRuleID)+1),vcsRuleID,vcsRuleName,vcsAmount, position)

    return render(request,'Badges/VirtualCurrencySpendRuleList.html', context_dict)

@login_required
def reorderVcSpendRuleList(request):
    context_dict,currentCourse = initialContextDict(request);

    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse).order_by('vcRulePosition')
    for rule in vcRules:
        if str(rule.vcRuleID) in request.POST:
            rule.vcRulePosition = request.POST[str(rule.vcRuleID)]
            rule.save()
    
    return virtualCurrencySpendRuleList(request)
