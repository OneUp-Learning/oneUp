from django.shortcuts import redirect

from Badges.models import ActionArguments, Conditions, Rules, RuleEvents, VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Badges.enums import Action, OperandTypes , Event, dict_dict_to_zipped_list
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required
from Instructors.constants import unlimited_constant

import logging
logger = logging.getLogger(__name__)

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

@login_required
def SaveVirtualCurrencySpendRule(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)
    
    if request.method == "POST": 
        if 'manual' in request.POST:
            logger.debug("Manual Spending Rule")
            if request.POST['vcRuleID']:
                DeleteVirtualCurrencySpendRule(request.POST['vcRuleID'])

            vcRuleInfo = VirtualCurrencyRuleInfo()
            logger.debug("New Spend Rule")
            
            condition = Conditions()
            condition.courseID = currentCourse
            condition.operation = '='
            condition.operand1Type = OperandTypes.immediateInteger
            condition.operand1Value = 1
            condition.operand2Type = OperandTypes.immediateInteger
            condition.operand2Value = 1
            condition.save()
                                            
            # Save game rule to the Rules table
            gameRule = Rules()
            gameRule.conditionID = condition
            gameRule.actionID = Action.decreaseVirtualCurrency
            gameRule.courseID = currentCourse
            gameRule.save()
            
            ruleEvent = RuleEvents()
            ruleEvent.rule = gameRule
            ruleEvent.event = Event.spendingVirtualCurrency
            ruleEvent.save()
            
            actionArgs = ActionArguments()
            actionArgs.ruleID = gameRule
            actionArgs.sequenceNumber = 1
            actionArgs.argumentValue = request.POST['ruleAmount'] if  not request.POST['ruleAmount'] == "" else str(0)
            actionArgs.save()
            
            vcRuleInfo.ruleID = gameRule    
            vcRuleInfo.vcRuleName = request.POST["ruleName"]
            vcRuleInfo.vcRuleDescription = request.POST["ruleDescription"]
            vcRuleInfo.vcRuleLimit = request.POST["ruleLimit"] if not request.POST['ruleLimit'] == "" else str(unlimited_constant)
            vcRuleInfo.vcRuleAmount = request.POST['ruleAmount'] if  not request.POST['ruleAmount'] == "" else str(0)
            vcRuleInfo.courseID = currentCourse
            vcRuleInfo.vcRuleType = False
            vcRuleInfo.save()  
        else:
            pass

            eventIndex = []
            eventName = []
            eventDescription = []
            eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description','isVirtualCurrencySpendRule'])  
            # Select only the system variables that are for virtual currency
            for i, eName, eDescription, eIsVirtualCurrencySpendRule in eventObjects:
                if eIsVirtualCurrencySpendRule:
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
                            rule.vcRuleAmount = int(actionArg.argumentValue)
                            rule.save()
                            selectedSpendRulesEvents.remove(eventI)
             
                else:
                    if eventI in selectedSpendRulesEvents:
                        vcRuleInfo = VirtualCurrencyRuleInfo()  
                    
                        # KI: As far as I can see, the following line (which I'm
                        # now commenting out) does this: since there is not rule
                        # for this rule check if any other virtual currency
                        # spending rule exists for this course and use that.
                        # Now, where this seems to break is that it means that
                        # we create extra RuleEvents and ActionArguments items
                        # for an existing rule which both fails to create a new
                        # rule and breaks things since at another place in the 
                        # code we assume that only one exists.
                        # For the moment, I'm just going to remove it and force
                        # things to the other case.
                        #gameRule = False

                        # The code now will create seperate rules, rules events, and 
                        # conditions for each new vc rule.
                        
                        condition = Conditions()
                        condition.courseID = currentCourse
                        condition.operation = '='
                        condition.operand1Type = OperandTypes.immediateInteger
                        condition.operand1Value = 1
                        condition.operand2Type = OperandTypes.immediateInteger
                        condition.operand2Value = 1
                        condition.save()
                                                        
                        # Save game rule to the Rules table
                        gameRule = Rules()
                        gameRule.conditionID = condition
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
                        vcRuleInfo.save()
                    
    return redirect("/oneUp/badges/VirtualCurrencySpendRuleList")