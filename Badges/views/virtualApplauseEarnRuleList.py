'''
Created on Nov 9, 2017

@author: Austin Hodge
'''

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from Badges.enums import OperandTypes
from Badges.models import (ActionArguments, Conditions, FloatConstants,
                           StringConstants,  VirtualApplauseRuleInfoo)
from Badges.systemVariables import SystemVariable
from Instructors.constants import unspecified_vc_manual_rule_name
from Instructors.views.utils import initialContextDict


@login_required
def virtualApplauseEarnRuleList(request):
    ## most of this page is repurposed code from VirtualCurrencyEarnRuleList 
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
                
    if 'isRuleCustom' in request.GET:
        vaRuleID = [] 
        vaRuleName = []
      
        position = []
        isRuleCustom = request.GET['isRuleCustom'] in ['true', 'True']
        
        if isRuleCustom == True:
            vaRulesCustom = VirtualApplauseRuleInfoo.objects.filter(vaRuleType=True, courseID=currentCourse).order_by('vaRulePosition')
            vaRules = [r for r in acRulesCustom if not hasattr(r, 'virtualapplauseruleinfo') and not hasattr(r, 'virtualapplauseperiodicrule')]
            
            for rule in vaRules:
                if rule.vaRuleName == unspecified_vc_manual_rule_name:
                    continue
                # Rules that are considered 'Earning' have vcRuleType as True
                vaRuleID.append(rule.vaRuleID)
                vaRuleName.append(rule.vaRuleName)
                # The custom earning rule amounts are not being used since 
                # Add VC to student transaction takes care of the amount 
                
                position.append(rule.vaRulePosition)
                
            context_dict['vaRuleInfo'] = zip(range(1,len(vaRuleID)+1),vaRuleID,vaRuleName, position)
        else:
            vaRules = VirtualApplauseRuleInfoo.objects.filter(courseID=currentCourse).order_by('vaRulePosition')
        
            for rule in vaRules:
                if rule.vaRuleName == unspecified_vc_manual_rule_name :
                    continue
                # Rules that are considered 'Earning' have vcRuleType as True
                
                vaRuleID.append(rule.vaRuleID)
                vaRuleName.append(rule.vaRuleName)
               
                position.append(rule.vaRulePosition)
               
               
           
            context_dict['vaRuleInfo'] = list(zip(range(1,len(vaRuleID)+1),vaRuleID,vaRuleName, position))
        
        context_dict['isRuleCustom'] = isRuleCustom
        context_dict['numRules'] = len(vaRuleID)

    return render(request,'Badges/VirtualApplauseEarnRuleList.html', context_dict)

@login_required
def reorderVirtualApplauseEarnRules(request):
    context_dict,currentCourse = initialContextDict(request);

    if request.POST['isRuleCustom'] == 'true':
        vaRulesCustom = VirtualApplauseRuleInfoo.objects.filter(vaRuleType=True, courseID=currentCourse).order_by('vaRulePosition')
        for rule in vaRulesCustom:
            if rule.vaRuleName == unspecified_vc_manual_rule_name:
                continue
            if str(rule.vaRuleID) in request.POST:
                rule.vaRulePosition = request.POST[str(rule.vaRuleID)]
                rule.save()
        
        return redirect('/oneUp/badges/VirtualApplauseEarnRuleList?isRuleCustom=true')
    else:
        vaRules = VirtualApplauseRuleInfoo.objects.filter(vaRuleType=True, courseID=currentCourse).order_by('vaRulePosition')
        for rule in vaRules:
            if rule.vaRuleName == unspecified_vc_manual_rule_name :
                continue
            if str(rule.vaRuleID) in request.POST:
                rule.vaRulePosition = request.POST[str(rule.vaRuleID)]
                rule.save()
    return redirect('/oneUp/badges/VirtualApplauseEarnRuleList?isRuleCustom=false')
