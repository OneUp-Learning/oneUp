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
from Badges.enums import Action, OperandTypes , SystemVariable, dict_dict_to_zipped_list
from Badges.conditions_util import get_events_for_system_variable, get_events_for_condition,\
    cond_from_mandatory_cond_list

from django.contrib.auth.decorators import login_required

def DeleteVirtualCurrencyRule(vcRuleID):

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

        # Check if creating a new badge or edit an existing one
        # If editing an existent one, we need to delete it first before saving the updated information in the database            
        if 'vcRuleID' in request.POST:   #edit or delete badge 
            print("Virtual Currency to Edit/Delete Id: "+str(request.POST['vcRuleID']))
            vcRuleInfo = VirtualCurrencyRuleInfo.objects.get(pk=int(request.POST['vcRuleID']))
            DeleteVirtualCurrencyRule(request.POST['vcRuleID'])
            if 'delete' in request.POST:
                return redirect("/oneUp/Badges/InstructorVirtualCurrencyList")
        else:
            vcRuleInfo = VirtualCurrencyRuleInfo()  # create new VC RuleInfo
                        
        if 'create' in request.POST or 'edit' in request.POST:
            # Get VC rule info
            vcRuleName = request.POST['ruleName'] # The entered Rule Name
            print("rule name: "+str(vcRuleName))
            vcRuleDescription = request.POST['ruleDescription'] # The entered Rule Description
            print("rule description: "+str(vcRuleDescription))
            vcRuleAmount = request.POST['ruleAmount'] # The entered Virtual Currency amount
            
            conditions = []
        
            sysIndex = []
            sysDisplayName = []
            
            systemVariableObjects= dict_dict_to_zipped_list(SystemVariable.systemVariables,['index','displayName'])  
            # Create list to loop through and select only the system variables that were selected
            for i, sysVars in systemVariableObjects:
                if sysVars in request.POST:
                        sysIndex.append(i)
                        sysDisplayName.append(sysVars)
            # Loop through all of the system variables.
            for index, sysVar in zip(sysIndex, sysDisplayName):                                
                # Create New Condition
                newCondition = Conditions()
                newCondition.operation = request.POST[str(sysVar)+'_operation']
                newCondition.operand1Type = OperandTypes.systemVariable
                newCondition.operand1Value = index
                print(sysVar+'_operation')
                print('newConditionOpenadType: (systemVariable)'+sysVar)
                print('newConditionOperand1Value: '+str(newCondition.operand1Value))
                print(sysVar+'_operand2Value')          
                newCondition.operand2Type = OperandTypes.immediateInteger
                newCondition.operand2Value = request.POST[sysVar+'_operand2Value']

               
                print('newCondition.operand2Type: '+str(newCondition.operand2Type))
                print('newCondition.operand2Value: '+str(newCondition.operand2Value))
                newCondition.save()
                
                conditions.append(newCondition)
            
            # If a particular challenge was specified, this needs to be added to the condition
            assignChallenges = str(request.POST['assignChallenges'])
            if (assignChallenges == '2'):
                specificChallenge = request.POST['specChallenge']
                challenge = Challenges.objects.get(challengeID=specificChallenge)
                challenge_cond = Conditions()
                challenge_cond.operation = '=='
                challenge_cond.operand1Type = OperandTypes.systemVariable
                challenge_cond.operand1Value = SystemVariable.challengeId
                challenge_cond.operand2Type = OperandTypes.immediateInteger
                challenge_cond.operand2Value = challenge.challengeID
                challenge_cond.save()
                conditions.append(challenge_cond)
                
            ruleCondition = cond_from_mandatory_cond_list(conditions)   
                
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
            vcRuleInfo.vcRuleType = True # Earning type
            vcRuleInfo.assignToChallenges = assignChallenges
            vcRuleInfo.save()
            
            ruleID = vcRuleInfo
            print("rule id: "+str(ruleID.vcRuleID))
            if not (ActionArguments.objects.filter(argumentValue=str(ruleID.vcRuleID)).exists()):
                # Save the action 'IncreaseVirtualCurrency' to the ActionArguments Table
                actionArgument = ActionArguments()
                actionArgument.ruleID = gameRule
                actionArgument.sequenceNumber = 1
                actionArgument.argumentValue =  vcRuleAmount
                actionArgument.save()
                
                
    return redirect("/oneUp/badges/InstructorVirtualCurrencyList")
    
