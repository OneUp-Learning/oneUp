'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Courses, Challenges
from Badges.models import ActionArguments, Conditions, Rules, Badges, RuleEvents
from Badges.enums import Action, Event, OperandTypes , SystemVariable
from Badges.conditions_util import get_events_for_system_variable, get_events_for_condition,\
    cond_from_mandatory_cond_list

from django.contrib.auth.decorators import login_required

def DeleteBadge(badgeId):

    # Delete the badge
    deleteBadges = Badges.objects.filter(badgeID=badgeId)
    for deleteBadge in deleteBadges:
        
        # The next line deletes the conditions and everything else related to the rule
        deleteBadge.ruleID.delete_related()
        # Then we delete the rule itself
        deleteBadge.ruleID.delete()
        # And then we delete the badge.
        deleteBadge.delete()

    actionArgs = ActionArguments.objects.filter(argumentValue=badgeId)
    for actionArg in actionArgs:
        actionArg.delete()

    # Delete  badge-challenges relationships from the BadgeChallenges table
#     badgeChalls = BadgeChallenges.objects.filter(badgeID=badgeId)
#     for chall in badgeChalls:
#         chall.delete()                     
            
def DetermineEvent(conditionOperandValue):
    # Note: This should be effectively removed soon and also can break for certain inputs.
    return get_events_for_system_variable(conditionOperandValue)[0]

def SaveBadge(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
    context_dict['course_Name'] = currentCourse.courseName
    
    if request.POST: 

        # Check if creating a new badge or edit an existing one
        # If editing an existent one, we need to delete it first before saving the updated information in the database            
        if 'badgeId' in request.POST:   #edit or delete badge 
            print("Badge to Edit/Delete Id: "+str(request.POST['badgeId']))
            badgeInformation = Badges.objects.get(pk=int(request.POST['badgeId']))
            DeleteBadge(request.POST['badgeId'])
        else:
            badgeInformation = Badges()  # create new badge
                        
        if 'create' in request.POST or 'edit' in request.POST:
            # Get badge info and the first condition
            badgeName = request.POST['badgeName'] # The entered Badge Name
            print("badge name: "+str(badgeName))
            badgeDescription = request.POST['badgeDescription'] # The entered Badge Description
            print("badge description: "+str(badgeDescription))
            badgeImage = request.POST['badgeImage'] # The Chosen Badge Image Name
            print("badge image: "+str(badgeImage))
            conditionOperand1Value = request.POST['cond1_operand1Value'] # The chosen system variable 
            print("cond1_operand1Value: "+str(conditionOperand1Value))
            conditionOperation = request.POST['cond1_operation'] # The chosen operation 
            print("cond1_operation: "+str(conditionOperation))
            print("cond1_operand2TypeSelector: " + request.POST['cond1_operand2TypeSelector'])
            if request.POST['cond1_operand2TypeSelector'] == 'constant':
                conditionOperand2Type = OperandTypes.immediateInteger
                conditionOperand2Value = request.POST['cond1_operand2Value'] 
                if  conditionOperand2Value =='':
                    conditionOperand2Value ='0'
            else:
                conditionOperand2Type =  OperandTypes.systemVariable   
                conditionOperand2Value = request.POST['cond1_operand2Variable']
            print("cond1_operand2Value: "+str(conditionOperand2Value))
        
            conditions = []
        
            print('numConds:'+request.POST['numConditions'])
            # Loop through all of the conditions.
            for i in range(1,int(request.POST['numConditions'])+1): 
                istr = str(i)                               
                # Create New Condition
                newCondition = Conditions()
                newCondition.operation = request.POST['cond'+istr+'_operation']
                newCondition.operand1Type = OperandTypes.systemVariable
                newCondition.operand1Value = request.POST['cond'+istr+'_operand1Value']
                print('newConditionOpenadType: systemVariable'+istr)
                print('newConditionOperand1Value: '+str(newCondition.operand1Value))
                
                # Check if the second operand is a constant or a system variable and assign the appropriate type and value of operand 
                if request.POST['cond'+istr+'_operand2TypeSelector'] == "constant":
                    newCondition.operand2Type = OperandTypes.immediateInteger
                    newCondition.operand2Value = request.POST['cond'+istr+'_operand2Value']
                else:
                    newCondition.operand2Type =  OperandTypes.systemVariable   
                    newCondition.operand2Value = request.POST['cond'+istr+'_operand2Variable']

                print('newCondition.operand2Type: '+str(newCondition.operand2Type))
                print('newCondition.operand2Value: '+str(newCondition.operand2Value))
                print("")
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
                
            badgeCondition = cond_from_mandatory_cond_list(conditions)   
                
            # Save game rule to the Rules table
            gameRule = Rules()
            gameRule.conditionID = badgeCondition
            gameRule.actionID = Action.giveBadge 
            gameRule.courseID = currentCourse
            gameRule.save()

            # We get all of the related events.
            events = get_events_for_condition(badgeCondition)
            for event in events:
                ruleEvent = RuleEvents()
                ruleEvent.rule = gameRule
                ruleEvent.event = event
                ruleEvent.save()

            # Save badge information to the Badges Table
            badgeInformation.ruleID = gameRule            
            badgeInformation.courseID = currentCourse
            badgeInformation.badgeName = badgeName
            badgeInformation.badgeDescription = badgeDescription
            badgeInformation.badgeImage = badgeImage
            badgeInformation.assignToChallenges = assignChallenges
            badgeInformation.save()
            
            badgeId = badgeInformation
            print("badge id: "+str(badgeId.badgeID))
            if not (ActionArguments.objects.filter(argumentValue=str(badgeId.badgeID)).exists()):
                # Save the action 'Giving a Badge' to the ActionArguments Table
                actionArgument = ActionArguments()
                actionArgument.ruleID = gameRule
                actionArgument.sequenceNumber = 1
                actionArgument.argumentValue =  badgeId.badgeID
                actionArgument.save()
                
            # The BadgeChallenges table is problematic because it moves information needed to evaluate the correctness
            # of a condition out of the condition itself and because the semantics of the association are unclear.
            # This idea (associating a badge with a group of specific challenges) is going on our TODO list, but
            # for right now does not make sense in the context of the existing Game engine.
            # As a result, all of the following code has been removed.
            # It has been replaced with code farther up above which assumes that at most one challenge can be
            # chosen.  The template has been changed to only allow that as well.
            #if (str(assignChallenges) == '2'):                   
            #    # Save the badge-challenges relationships to the BadgeChallenges table
            #    assignToChallenges = request.POST.getlist('specChallenges')
            #    for j in range(0,len(assignToChallenges)):
            #        badgeChallenge = BadgeChallenges()
            #        badgeChallenge.badgeID = badgeId
            #        badgeChallenge.challengeID = Challenges.objects.get(challengeID=assignToChallenges[j])
            #        badgeChallenge.save()
            #        print("Print the specific challenges: ")
            #        print(str(badgeChallenge))
            #            
            #elif (str(assignChallenges) == '1'):
            #    # Save the badge-challenges relationships to the BadgeChallenges table
            #    allChallenges = Challenges.objects.all()
            #    for challenge in allChallenges:
            #        badgeChallenge = BadgeChallenges()
            #        badgeChallenge.badgeID = badgeId
            #        badgeChallenge.challengeID = challenge
            #        badgeChallenge.save()
                
    return redirect("/oneUp/badges/Badges")
    
