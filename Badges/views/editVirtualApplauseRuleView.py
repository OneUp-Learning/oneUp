'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

from Badges.models import VirtualApplauseRuleInfo,VirtualApplauseCustomRuleInfo, ActionArguments

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import setUpContextDictForConditions, databaseConditionToJSONString
from Instructors.views.utils import initialContextDict
from Badges.systemVariables import logger

@login_required
def EditVirtualApplauseRule(request):
    ## most of this page is repurposed code from editVirtualCurrencyEarnRuleView
    context_dict,currentCourse = initialContextDict(request);
        
    if request.GET:

        # Getting the Rule information which has been selected
        if request.GET['vaRuleID']:
            vaRuleID = request.GET['vaRuleID']
            isRuleCustom = request.GET['isRuleCustom'] in ['true', 'True']
            logger.debug("[GET] isRuleCustom " + str(isRuleCustom))
            if isRuleCustom == True:
               
                rule = VirtualApplauseCustomRuleInfo.objects.get(vaRuleID=vaRuleID, courseID=currentCourse)
                                    
                context_dict = setUpContextDictForConditions(context_dict,currentCourse,None)

            else:
                rule = VirtualApplauseRuleInfo.objects.get(vaRuleID=vaRuleID, courseID=currentCourse)
                
                context_dict = setUpContextDictForConditions(context_dict,currentCourse,rule.ruleID)
                    
                if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                    context_dict["vaAmount"] = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
                else:
                    context_dict["vaAmount"] = 0
                    
            context_dict['isRuleCustom'] = isRuleCustom
        else:
            context_dict = setUpContextDictForConditions(context_dict,currentCourse,None)

    # The range part is the index numbers.
    context_dict['vaRule'] = rule
    
    context_dict['editOrCreate']="edit"
    context_dict['capitalEditOrCreate']="Edit"
    context_dict['saveOrCreate']="save"
    context_dict['captialSaveOrCreate'] = "Save"

    return render(request,'Badges/EditVirtualApplauseRule.html', context_dict)