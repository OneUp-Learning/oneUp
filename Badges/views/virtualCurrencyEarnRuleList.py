'''
Created on Nov 9, 2017

@author: Austin Hodge
'''

from django.shortcuts import render, redirect 

from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo, ActionArguments, Conditions, FloatConstants, StringConstants
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
                
    if 'isRuleCustom' in request.GET:
        vcRuleID = [] 
        vcRuleName = []
        vcRuleDescription = []
        vcAmount = []
        position = []
        isRuleCustom = request.GET['isRuleCustom'] in ['true', 'True']
        
        if isRuleCustom == True:
            vcRulesCustom = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=True, courseID=currentCourse).order_by('vcRulePosition')
            vcRules = [r for r in vcRulesCustom if not hasattr(r, 'virtualcurrencyruleinfo') and not hasattr(r, 'virtualcurrencyperiodicrule')]
            
            for rule in vcRules:
                # Rules that are considered 'Earning' have vcRuleType as True
                vcRuleID.append(rule.vcRuleID)
                vcRuleName.append(rule.vcRuleName)
                # The custom earning rule amounts are not being used since 
                # Add VC to student transaction takes care of the amount 
                vcAmount.append(rule.vcRuleAmount)
                vcRuleDescription.append(rule.vcRuleDescription)
                position.append(rule.vcRulePosition)
                
            context_dict['vcRuleInfo'] = zip(range(1,len(vcRuleID)+1),vcRuleID,vcRuleName,vcRuleDescription, vcAmount, position)
        else:
            vcRules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=True, courseID=currentCourse).order_by('vcRulePosition')
            
            for rule in vcRules:
                # Rules that are considered 'Earning' have vcRuleType as True
                if rule.vcRuleType == True:
                    vcRuleID.append(rule.vcRuleID)
                    vcRuleName.append(rule.vcRuleName)
                    vcRuleDescription.append(rule.vcRuleDescription)
                    position.append(rule.vcRulePosition)
                    if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                        vcAmount.append(ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue)
                    else:
                        vcAmount.append(0)
                            
            context_dict['vcRuleInfo'] = zip(range(1,len(vcRuleID)+1),vcRuleID,vcRuleName,vcRuleDescription,vcAmount, position)
            
        context_dict['isRuleCustom'] = isRuleCustom
        context_dict['numRules'] = len(vcRuleID)

    return render(request,'Badges/VirtualCurrencyEarnRuleList.html', context_dict)

@login_required
def reorderVirtualCurrencyEarnRules(request):
    context_dict,currentCourse = initialContextDict(request);

    if request.POST['isRuleCustom'] == 'true':
        vcRulesCustom = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=True, courseID=currentCourse).order_by('vcRulePosition')
        for rule in vcRulesCustom:
            if str(rule.vcRuleID) in request.POST:
                rule.vcRulePosition = request.POST[str(rule.vcRuleID)]
                rule.save()
        
        return redirect('/oneUp/badges/VirtualCurrencyEarnRuleList?isRuleCustom=true')
    else:
        vcRules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=True, courseID=currentCourse).order_by('vcRulePosition')
        for rule in vcRules:
            if str(rule.vcRuleID) in request.POST:
                rule.vcRulePosition = request.POST[str(rule.vcRuleID)]
                rule.save()
        return redirect('/oneUp/badges/VirtualCurrencyEarnRuleList?isRuleCustom=false')


    
