'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo,VirtualCurrencyCustomRuleInfo, ActionArguments

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import setUpContextDictForConditions, databaseConditionToJSONString
from Instructors.views.utils import initialContextDict
from Badges.systemVariables import logger

@login_required
def EditVirtualCurrencyRule(request):
 
    context_dict,currentCourse = initialContextDict(request);
        
    if request.GET:

        # Getting the Rule information which has been selected
        if request.GET['vcRuleID']:
            vcRuleID = request.GET['vcRuleID']
            isRuleCustom = request.GET['isRuleCustom'] in ['true', 'True']
            logger.debug("[GET] isRuleCustom " + str(isRuleCustom))
            if isRuleCustom == True:
               
                rule = VirtualCurrencyCustomRuleInfo.objects.get(vcRuleID=vcRuleID, courseID=currentCourse)
                context_dict["vcAmount"] = rule.vcRuleAmount
                if rule.vcAmountVaries:
                    context_dict["vcAmountVaries"] = "checked"
                else:
                    context_dict["vcAmountVaries"]=""
                    
                context_dict = setUpContextDictForConditions(context_dict,currentCourse,None)

            else:
                rule = VirtualCurrencyRuleInfo.objects.get(vcRuleID=vcRuleID, courseID=currentCourse)
                
                context_dict = setUpContextDictForConditions(context_dict,currentCourse,rule.ruleID)
                    
                if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                    context_dict["vcAmount"] = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
                else:
                    context_dict["vcAmount"] = 0
                    
            context_dict['isRuleCustom'] = isRuleCustom
        else:
            context_dict = setUpContextDictForConditions(context_dict,currentCourse,None)

    # The range part is the index numbers.
    context_dict['vcRule'] = rule
    
    context_dict['editOrCreate']="edit"
    context_dict['capitalEditOrCreate']="Edit"
    context_dict['saveOrCreate']="save"
    context_dict['captialSaveOrCreate'] = "Save"

    
    return render(request,'Badges/EditVirtualCurrencyRule.html', context_dict)