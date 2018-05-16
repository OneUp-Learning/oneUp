'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Courses, Challenges
from Badges.models import ActionArguments, Conditions, Rules, RuleEvents, VirtualCurrencyRuleInfo
from Badges.enums import Action, OperandTypes , Event, dict_dict_to_zipped_list
from Badges.conditions_util import get_events_for_system_variable, get_events_for_condition,\
    cond_from_mandatory_cond_list
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required
from Badges.systemVariables import logger

def DeleteVirtualCurrencySpendRule(vcRuleID):
    vcRuleID = int(vcRuleID)
    # Delete the Virtual Currency Rule 
    deleteVc = VirtualCurrencyRuleInfo.objects.get(vcRuleID=vcRuleID)
    # The next line deletes the conditions and everything else related to the rule
    deleteVc.ruleID.delete_related()
    # Then we delete the rule itself
    deleteVc.ruleID.delete()
    # And then we delete the badge.
    deleteVc.delete()
            
def DetermineEvent(conditionOperandValue):
    # Note: This should be effectively removed soon and also can break for certain inputs.
    return get_events_for_system_variable(conditionOperandValue)[0]

def SaveVirtualCurrencySpendRule(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)
    
    if request.method == "POST": 
        eventIndex = []
        eventName = []
        eventDescription = []
        eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description'])  
        # Select only the system variables that are for virtual currency
        for i, eName, eDescription in eventObjects:
            if i>= 850:
                eventIndex.append(i)
                eventName.append(eName)
                eventDescription.append(eDescription)
                
        selectedSpendRulesEvents = list(map(int,request.POST.getlist('spendRules')))
        for  eventI, eventN, eventD in zip(eventIndex, eventName, eventDescription):
            vcRules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False,ruleID__ruleevents__event=eventI, courseID=currentCourse)
            if vcRules: # If there is a rule created with this event
                for rule in vcRules:
                    if eventI not in selectedSpendRulesEvents:
                        DeleteVirtualCurrencySpendRule(rule.vcRuleID)
                        continue
                    # Update the rule
                    if eventI in selectedSpendRulesEvents:
                        rule.vcRuleName = request.POST["ruleName_"+str(eventI)]
                        rule.vcRuleDescription = request.POST["ruleDescription_"+str(eventI)]
                        rule.vcRuleLimit = request.POST["ruleLimit_"+str(eventI)]
                        if ActionArguments.objects.filter(ruleID=rule.ruleID).exists():
                            actionArg = ActionArguments.objects.get(ruleID=rule.ruleID)
                        else:
                            actionArg = ActionArguments()
                            actionArg.ruleID = rule.ruleID
                            actionArg.sequenceNumber = 1
                        
                        actionArg.argumentValue = request.POST["ruleAmount_"+str(eventI)]
                        actionArg.save()
                        rule.save()
                        selectedSpendRulesEvents.remove(eventI)
            else:
                if eventI in selectedSpendRulesEvents:
                    vcRuleInfo = VirtualCurrencyRuleInfo()  
                    
                    newCondition = Conditions()
                    newCondition.courseID = currentCourse
                    newCondition.operation = '='
                    newCondition.operand1Type = OperandTypes.immediateInteger
                    newCondition.operand1Value = 1
                    newCondition.operand2Type = OperandTypes.immediateInteger
                    newCondition.operand2Value = 1
                    newCondition.save()
                                
                    ruleCondition = cond_from_mandatory_cond_list([newCondition])
                
                    # Save game rule to the Rules table
                    gameRule = Rules()
                    gameRule.conditionID = ruleCondition
                    gameRule.actionID = Action.decreaseVirtualCurrency
                    gameRule.courseID = currentCourse
                    gameRule.save()
                    
                    ruleEvent = RuleEvents()
                    ruleEvent.rule = gameRule
                    ruleEvent.event = eventI
                    ruleEvent.save()
                    
                    actionArgs = ActionArguments()
                    actionArgs.ruleID = gameRule
                    actionArgs.sequenceNumber = 1
                    actionArgs.argumentValue = request.POST["ruleAmount_"+str(eventI)]
                    actionArgs.save()
                    
                    vcRuleInfo.ruleID = gameRule            
                    vcRuleInfo.courseID = currentCourse
                    vcRuleInfo.vcRuleName = request.POST["ruleName_"+str(eventI)]
                    vcRuleInfo.vcRuleDescription = request.POST["ruleDescription_"+str(eventI)]
                    vcRuleInfo.vcRuleLimit = request.POST["ruleLimit_"+str(eventI)]
                    vcRuleInfo.vcRuleAmount = request.POST["ruleAmount_"+str(eventI)]
                    vcRuleInfo.vcRuleType = False # Spending type
                    vcRuleInfo.assignToChallenges = 1
                    vcRuleInfo.save()
                
    return redirect("/oneUp/badges/VirtualCurrencySpendRuleList")
    
