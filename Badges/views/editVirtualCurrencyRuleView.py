'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import setUpContextDictForConditions, databaseConditionToJSONString
from Instructors.views.utils import initialContextDict

@login_required
def EditVirtualCurrencyRule(request):
 
    context_dict,currentCourse = initialContextDict(request);

    context_dict = setUpContextDictForConditions(context_dict,currentCourse)
        
    if request.GET:

        # Getting the Rule information which has been selected
        if request.GET['vcRuleID']:
            vcRuleID = request.GET['vcRuleID']
            rule = VirtualCurrencyRuleInfo.objects.get(vcRuleID=vcRuleID, courseID=currentCourse)
            
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                context_dict["vcAmount"] = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
            else:
                context_dict["vcAmount"] = 0
                
            condition = rule.ruleID.conditionID
            print("Condition: "+str(condition))
                 
            context_dict['initialCond'] = databaseConditionToJSONString(condition)           

    # The range part is the index numbers.
    context_dict['vcRule'] = rule
    
    context_dict['editOrCreate']="edit"
    context_dict['capitalEditOrCreate']="Edit"
    context_dict['saveOrCreate']="save"
    context_dict['captialSaveOrCreate'] = "Save"

    
    return render(request,'Badges/EditVirtualCurrencyRule.html', context_dict)