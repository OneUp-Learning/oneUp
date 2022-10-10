'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Courses, Challenges, Activities
from Badges.models import ActionArguments, Conditions, Rules, RuleEvents, VirtualApplauseRuleInfoo
from Badges.enums import Action, OperandTypes, dict_dict_to_zipped_list,    AwardFrequency, ApplauseOption
from Badges.systemVariables import SystemVariable
from Badges.conditions_util import get_events_for_condition, stringAndPostDictToCondition

from django.contrib.auth.decorators import login_required

def DeleteVirtualApplauseRule(vaRuleID, isRuleCustom):
    ## most of this page is repurposed code from saveVirtualCurrencyRule
    print("delete")
    if isRuleCustom == True:
        # Delete the Virtual applause Rule 
        deleteVa = VirtualApplauseRuleInfoo.objects.filter(vaRuleID=vaRuleID)
        for deleteVa in deleteVa:
            deleteVa.delete()
    else:
        deleteVa = VirtualApplauseRuleInfoo.objects.filter(vaRuleID=vaRuleID)
       
        for deleteVa in deleteVa:
                        
            # The next line deletes the conditions and everything else related to the rule
            deleteVa.ruleID.delete_related()
            # Then we delete the rule itself
            deleteVa.ruleID.delete()
            # And then we delete the badge.
            deleteVa.delete()

def SaveVirtualApplauseRule(request):
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
            print("Virtual Applause to Edit/Delete Id: "+str(request.POST['vaRuleID']))
            if isRuleCustom == True:
                vaRuleInfo = VirtualApplauseRuleInfoo.objects.get(pk=int(request.POST['vaRuleID']))
            else:
                vaRuleInfo = VirtualApplauseRuleInfoo.objects.get(pk=int(request.POST['vaRuleID']))
         
            if 'delete' in request.POST:
                DeleteVirtualApplauseRule(request.POST['vaRuleID'], isRuleCustom)
                return redirect("/oneUp/badges/VirtualApplauseEarnRuleList?isRuleCustom="+str(isRuleCustom))
        else:
            if isRuleCustom == True:
                vaRuleInfo = VirtualApplauseRuleInfoo() 
            else:
                vaRuleInfo = VirtualApplauseRuleInfoo()  # create new va RuleInfo
            
                  
        if 'create' in request.POST or 'edit' in request.POST:
            # Get va rule info
            vaRuleName = request.POST['ruleName'] # The entered Rule Name
         
            print("rule name: "+str(vaRuleName))
           
            # The custom earning rule amounts are not being used since 
            # Add va to student transaction takes care of the amount

            # The entered Virtual applause amount
            #vaRuleAmount = 0
         
              #  print(context_dict['vaAmount'])
            vaOption = request.POST["vaOption"]
            
            if isRuleCustom == True:                    
                # Save rule information to the VirtualapplauseRuleInfo Table
                vaRuleInfo.courseID =    currentCourse
                vaRuleInfo.vaRuleName = vaRuleName
                vaRuleInfo.ApplauseOption = vaOption     
                vaRuleInfo.save()
            else:
                if 'edit' in request.POST:
                    oldRuleToDelete = vaRuleInfo.ruleID
                    

                ruleCondition = stringAndPostDictToCondition(request.POST['cond-cond-string'],request.POST,currentCourse)
                    
                # Save game rule to the Rules table
                gameRule = Rules()
                gameRule.conditionID = ruleCondition
                gameRule.actionID = Action.DoApplause
                gameRule.courseID = currentCourse
                
                awardFreq = int(request.POST['awardFrequency'])
                gameRule.awardFrequency = awardFreq
                
                gameRule.objectSpecifier = request.POST['chosenObjectSpecifierString'];
                gameRule.save()
    
                # We get all of the related events.
                context = AwardFrequency.awardFrequency[awardFreq]['objectType']
                events = get_events_for_condition(ruleCondition,context)
                for event, isGlobal in events:
                    ruleEvent = RuleEvents()
                    ruleEvent.rule = gameRule
                    ruleEvent.event = event
                    ruleEvent.inGlobalContext = isGlobal
                    ruleEvent.save()
    
                # Save rule information to the VirtualapplauseRuleInfo Table
                vaRuleInfo.ruleID = gameRule            
                vaRuleInfo.courseID = currentCourse
                vaRuleInfo.vaRuleName = vaRuleName
                if( len(vaOption) == 0 ):
                    vaOption = ApplauseOption.random
                vaRuleInfo.ApplauseOption = vaOption 
                
                vaRuleInfo.awardFrequency = int(request.POST['awardFrequency'])
                vaRuleInfo.save()

                ruleID = vaRuleInfo
                print("rule id: "+str(ruleID.vaRuleID))
                if not (ActionArguments.objects.filter(ruleID=gameRule).exists()):
                    # Save the action 'IncreaseVirtualapplause' to the ActionArguments Table
                    actionArgument = ActionArguments()
                    actionArgument.ruleID = gameRule
                    actionArgument.sequenceNumber = 1
                
                    actionArgument.save()

                if 'edit' in request.POST:
                    oldRuleToDelete.delete_related()
                    oldRuleToDelete.delete()
                 
    return redirect("/oneUp/badges/VirtualApplauseEarnRuleList?isRuleCustom="+str(isRuleCustom))
    
