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

from django.contrib.auth.decorators import login_required

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
    
    actionArgs = ActionArguments.objects.filter(ruleID=deleteVc.ruleID)
    for actionArg in actionArgs:
        actionArg.delete()  
            
def DetermineEvent(conditionOperandValue):
    # Note: This should be effectively removed soon and also can break for certain inputs.
    return get_events_for_system_variable(conditionOperandValue)[0]

def SaveVirtualCurrencySpendRule(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
    context_dict['course_Name'] = currentCourse.courseName
    
    if request.POST: 

        # Delete the spend rule
        if 'delete' in request.POST:
            DeleteVirtualCurrencySpendRule(request.POST['vcsRuleID'])
            return redirect("/oneUp/badges/InstructorVirtualCurrencyList")            
        
        if 'create' in request.POST or 'edit' in request.POST:
                
            eventIndex = []
            eventName = []
            eventDescription = []
            eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description'])  
            # Select only the system variables that are for virtual currency
            for i, eName, eDescription in eventObjects:
                if eName in request.POST and i>= 850:
                    eventIndex.append(i)
                    eventName.append(eName)
                    eventDescription.append(eDescription)
                    
            
            vcRules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False)
            for rule in vcRules:
                found = False
                for  eventI, eventN, eventD in zip(eventIndex, eventName, eventDescription):
                    if rule.vcRuleName == eventN:
                        vcRuleInfo = VirtualCurrencyRuleInfo.objects.get(vcRuleName = eventN)
                        found = True
                if found == False:
                    # Delete the rule
                    DeleteVirtualCurrencySpendRule(rule.vcRuleID)
                    
            # Loop through all of the system variables.
            for eventI, eventN, eventD in zip(eventIndex, eventName, eventDescription):
                found = False  
                conditions = []
                for rule in vcRules:
                    if rule.vcRuleName == eventN:
                        vcRuleInfo = VirtualCurrencyRuleInfo.objects.get(vcRuleName = eventN)
                        print("found: " + str(vcRuleInfo.vcRuleName))
                        found = True
                        break
                if found == False:
                    vcRuleInfo = VirtualCurrencyRuleInfo()  # create new VC RuleInfo
                    # Create New Condition (Template condition(1 == 1) because no condition is required for this rule)
                    newCondition = Conditions()
                    newCondition.courseID = currentCourse
                    newCondition.operation = '='
                    newCondition.operand1Type = OperandTypes.immediateInteger
                    newCondition.operand1Value = 1
                    newCondition.operand2Type = OperandTypes.immediateInteger
                    newCondition.operand2Value = 1
                    newCondition.save()
                    
                    conditions.append(newCondition)
                    
                    ruleCondition = cond_from_mandatory_cond_list(conditions)
                
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
                    actionArgs.argumentValue = request.POST[eventN+"_Value"]
                    print("eventName: " + str(eventN) + " eventD: " + str(eventD) + " eventValue: " + request.POST[eventN+"_Value"])  
                    actionArgs.save()
                    
                    vcRuleInfo.ruleID = gameRule            
                    vcRuleInfo.courseID = currentCourse
                    vcRuleInfo.vcRuleName = eventN
                    vcRuleInfo.vcRuleDescription = eventD
                    vcRuleInfo.vcRuleAmount = int(request.POST[eventN+"_Value"])
                    vcRuleInfo.vcRuleType = False # Spending type
                    vcRuleInfo.assignToChallenges = 1
                    vcRuleInfo.save()
                else:
                    
                    actionArgs = ActionArguments.objects.get(ruleID=vcRuleInfo.ruleID)
                    actionArgs.argumentValue = request.POST[eventN+"_Value"]
                    print("eventName: " + str(eventN) + " eventD: " + str(eventD) + " eventValue: " + request.POST[eventN+"_Value"])  
                    actionArgs.save()
                    
                
                
    return redirect("/oneUp/badges/VirtualCurrencySpendRuleList")
    
