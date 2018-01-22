'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Courses, Challenges, Activities
from Badges.models import ActionArguments, Conditions, Rules, RuleEvents, VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Badges.enums import Action, OperandTypes, dict_dict_to_zipped_list
from Badges.systemVariables import SystemVariable
from Badges.conditions_util import get_events_for_system_variable, get_events_for_condition,\
    cond_from_mandatory_cond_list, stringAndPostDictToCondition

from django.contrib.auth.decorators import login_required

def DeleteVirtualCurrencyRule(vcRuleID, isRuleCustom):

    if isRuleCustom == True:
        # Delete the Virtual Currency Rule 
        deleteVC = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleID=vcRuleID)
        for deleteVc in deleteVC:
            deleteVc.delete()
    else:
        # Delete the Virtual Currency Rule 
        deleteVC = VirtualCurrencyRuleInfo.objects.filter(vcRuleID=vcRuleID)
        for deleteVc in deleteVC:
            
            # The next line deletes the conditions and everything else related to the rule
            deleteVc.ruleID.delete_related()
            # Then we delete the rule itself
            deleteVc.ruleID.delete()
            # And then we delete the badge.
            deleteVc.delete()
    
        actionArgs = ActionArguments.objects.filter(argumentValue=vcRuleID)
        for actionArg in actionArgs:
            actionArg.delete()
                    
            
def DetermineEvent(conditionOperandValue):
    # Note: This should be effectively removed soon and also can break for certain inputs.
    return get_events_for_system_variable(conditionOperandValue)[0]

def SaveVirtualCurrencyRule(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
    context_dict['course_Name'] = currentCourse.courseName
    
    if request.POST: 
        isRuleCustom = request.POST['isRuleCustom'] in ['true', 'True']
        # Check if creating a new badge or edit an existing one
        # If editing an existent one, we need to delete it first before saving the updated information in the database            
        if 'edit' in request.POST:   #edit or delete badge 
            print("Virtual Currency to Edit/Delete Id: "+str(request.POST['vcRuleID']))
            if isRuleCustom == True:
                vcRuleInfo = VirtualCurrencyCustomRuleInfo.objects.get(pk=int(request.POST['vcRuleID']))
            else:
                vcRuleInfo = VirtualCurrencyRuleInfo.objects.get(pk=int(request.POST['vcRuleID']))
            if 'delete' in request.POST:
                DeleteVirtualCurrencyRule(request.POST['vcRuleID'], isRuleCustom)
                return redirect("/oneUp/badges/VirtualCurrencyEarnRuleList?isRuleCustom="+str(isRuleCustom))
        else:
            if isRuleCustom == True:
                vcRuleInfo = VirtualCurrencyCustomRuleInfo()  # create new VC Custom RuleInfo
            else:
                vcRuleInfo = VirtualCurrencyRuleInfo()  # create new VC RuleInfo
            
                        
        if 'create' in request.POST or 'edit' in request.POST:
            # Get VC rule info
            vcRuleName = request.POST['ruleName'] # The entered Rule Name
            print("rule name: "+str(vcRuleName))
            vcRuleDescription = request.POST['ruleDescription'] # The entered Rule Description
            print("rule description: "+str(vcRuleDescription))

            vcRuleAmount = request.POST['ruleAmount'] # The entered Virtual Currency amount
                
            if isRuleCustom == True:                    
                # Save rule information to the VirtualCurrencyRuleInfo Table
                vcRuleInfo.courseID = currentCourse
                vcRuleInfo.vcRuleName = vcRuleName
                vcRuleInfo.vcRuleDescription = vcRuleDescription
                vcRuleInfo.vcRuleAmount = vcRuleAmount
                vcRuleInfo.save()
            else:
                if 'edit' in request.POST:
                    oldRuleToDelete = vcRuleInfo.ruleID

                ruleCondition = stringAndPostDictToCondition(request.POST['cond-cond-string'],request.POST,currentCourse)
                    
                # Save game rule to the Rules table
                gameRule = Rules()
                gameRule.conditionID = ruleCondition
                gameRule.actionID = Action.increaseVirtualCurrency
                gameRule.courseID = currentCourse
                gameRule.save()
    
                # We get all of the related events.
                events = get_events_for_condition(ruleCondition)
                for event in events:
                    ruleEvent = RuleEvents()
                    ruleEvent.rule = gameRule
                    ruleEvent.event = event
                    ruleEvent.save()
    
                # Save rule information to the VirtualCurrencyRuleInfo Table
                vcRuleInfo.ruleID = gameRule            
                vcRuleInfo.courseID = currentCourse
                vcRuleInfo.vcRuleName = vcRuleName
                vcRuleInfo.vcRuleDescription = vcRuleDescription
                vcRuleInfo.vcRuleAmount = -1                # Added on 01/18/18  by DD
                vcRuleInfo.vcRuleType = True # Earning type
                vcRuleInfo.vcRuleAmount = -1                # Added on 01/18/18  by DD
                vcRuleInfo.assignToChallenges = 0 # We should delete this from the model soon.
                vcRuleInfo.awardFrequency = int(request.POST['awardFrequency'])
                vcRuleInfo.save()

                ruleID = vcRuleInfo
                print("rule id: "+str(ruleID.vcRuleID))
                if not (ActionArguments.objects.filter(ruleID=gameRule).exists()):
                    # Save the action 'IncreaseVirtualCurrency' to the ActionArguments Table
                    actionArgument = ActionArguments()
                    actionArgument.ruleID = gameRule
                    actionArgument.sequenceNumber = 1
                    actionArgument.argumentValue =  vcRuleAmount
                    actionArgument.save()

                if 'edit' in request.POST:
                    oldRuleToDelete.delete()
                
    return redirect("/oneUp/badges/VirtualCurrencyEarnRuleList?isRuleCustom="+str(isRuleCustom))
    
