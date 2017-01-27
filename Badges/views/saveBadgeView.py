'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Courses, Challenges
from Badges.models import ActionArguments, Conditions, Rules, Badges, BadgeChallenges, RuleEvents
from Badges.enums import Action, Event, OperandTypes , SystemVariable

from django.contrib.auth.decorators import login_required

def DeleteBadge(badgeId):

    # Delete the badge
    deleteBadges = Badges.objects.filter(badgeID=badgeId)
    for deleteBadge in deleteBadges:
        deleteBadge.ruleID.delete_related()
        deleteBadge.ruleID.delete()
        deleteBadge.delete()

    actionArgs = ActionArguments.objects.filter(argumentValue=badgeId)
    for actionArg in actionArgs:
        actionArg.delete()

    # Delete  badge-challenges relationships from the BadgeChallenges table
    badgeChalls = BadgeChallenges.objects.filter(badgeID=badgeId)
    for chall in badgeChalls:
        chall.delete()                     
            
    # Delete conditions
            
    # Delete associated rule
    
def DetermineEvent(conditionOperandValue):
    
    #Determine the appropriate event type for each System Variable
    if int(conditionOperandValue) == SystemVariable.numAttempts:
        #eventID = Event.startChallenge
        eventID = Event.endChallenge
    elif int(conditionOperandValue) == SystemVariable.testScore:
        eventID = Event.endChallenge
    elif int(conditionOperandValue) == SystemVariable.percentageCorrect:
        eventID = Event.endChallenge
    elif int(conditionOperandValue) == SystemVariable.maxTestScore:
        eventID = Event.challengeExpiration
    elif int(conditionOperandValue) == SystemVariable.minTestScore:
        eventID = Event.challengeExpiration
    elif int(conditionOperandValue) == SystemVariable.dateOfFirstAttempt:
        eventID = Event.startChallenge
    elif int(conditionOperandValue) == SystemVariable.timeSpentOnChallenges:
        eventID = Event.endChallenge
    elif int(conditionOperandValue) == SystemVariable.timeSpentOnQuestions:
        eventID = Event.endQuestion
    elif int(conditionOperandValue) == SystemVariable.consecutiveDaysLoggedIn:
        eventID = Event.userLogin
    elif int(conditionOperandValue) == SystemVariable.activitiesCompleted:
        eventID = Event.participationNoted
    elif int(conditionOperandValue) == SystemVariable.challengeId:
        eventID = Event.endChallenge #Not sure what the appropriate event would be for this system variable
    return eventID
    
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
            else:
                conditionOperand2Type =  OperandTypes.systemVariable   
                conditionOperand2Value = request.POST['cond1_operand2Variable']
            print("cond1_operand2Value: "+str(conditionOperand2Value))
            
            assignToChallenges = []
            if(request.POST['assignChallenges'] == 2):
                specificChallenges = request.POST['specChallenges']
                print("specific challenges: "+str(specificChallenges))
            assignChallenges = request.POST['assignChallenges'] # The chosen challenges to assign the badge
            print("assign to challenges: "+str(assignChallenges))
                        
            # Save the entered condition to the Conditions table
            badgeCondition = Conditions()
            badgeCondition.operation = conditionOperation
            badgeCondition.operand1Type = OperandTypes.systemVariable
            badgeCondition.operand1Value = conditionOperand1Value
            badgeCondition.operand2Type = conditionOperand2Type
            badgeCondition.operand2Value = conditionOperand2Value
            badgeCondition.save()
        
            # Loop if there are more than one condition. Creates a chain of ANDs
            #   ( looks like AND
            #                /  \
            #               AND  cond3
            #              /   \
            #          cond1   cond2
            for i in range(1,int(request.POST['numConditions'])):
                print( 'numConditions ' + request.POST['numConditions'])
                oldCondition = badgeCondition
                                
                # Create New Condition
                iplusone = i+1
                newCondition = Conditions()
                newCondition.operation = request.POST['cond'+str(iplusone)+'_operation']
                newCondition.operand1Type = OperandTypes.systemVariable
                newCondition.operand1Value = request.POST['cond'+str(iplusone)+'_operand1Value']
                print('newConditionOpenadType: systemVariable'+str(iplusone))
                print('newConditionOperand1Value: '+str(newCondition.operand1Value))
                
                # Check if the second operand is a constant or a system variable and assign the appropriate type and value of operand 
                if request.POST['cond'+str(iplusone)+'_operand2TypeSelector'] == "constant":
                    newCondition.operand2Type = OperandTypes.immediateInteger
                    newCondition.operand2Value = request.POST['cond'+str(iplusone)+'_operand2Value']
                else:
                    newCondition.operand2Type =  OperandTypes.systemVariable   
                    newCondition.operand2Value = request.POST['cond'+str(iplusone)+'_operand2Variable']

                print('newCondition.operand2Type: '+str(newCondition.operand2Type))
                print('newCondition.operand2Value: '+str(newCondition.operand2Value))
                print("")
                newCondition.save()
                
                # Create AND condition last
                badgeCondition = Conditions()
                badgeCondition.operation = "AND"
                badgeCondition.operand1Type = OperandTypes.condition
                badgeCondition.operand1Value = oldCondition.conditionID
                badgeCondition.operand2Type = OperandTypes.condition
                badgeCondition.operand2Value = newCondition.conditionID             
                badgeCondition.save()
                print("AND: oldCondition (condition 1st operand): "+str(oldCondition.operand1Value))
                print("AND: newCondition (condition 2nd operand): "+str(newCondition.operand1Value))
                #print("badgeCondition: "+str(badgeCondition.operand1Value))
                
            #PRINT ALL BADGE CONDITIONS AND THEIR CORRESPONDING NUMBERS
            #NEED TO CREATE "LIST" OF RULES FOR EACH BADGE 
            #(i.e. a single badge should be able to support multiple rules)     
                
            # Save game rule to the Rules table
            gameRule = Rules()
            gameRule.conditionID = badgeCondition
#            gameRule.eventID = DetermineEvent(conditionOperand1Value)
            gameRule.actionID = Action.giveBadge 
            gameRule.courseID = currentCourse
            gameRule.save()

            ruleEvent = RuleEvents()
            ruleEvent.rule = gameRule
            ruleEvent.event = DetermineEvent(conditionOperand1Value)

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
            
            if (str(assignChallenges) == '2'):                   
                # Save the badge-challenges relationships to the BadgeChallenges table
                assignToChallenges = request.POST.getlist('specChallenges')
                for j in range(0,len(assignToChallenges)):
                    badgeChallenge = BadgeChallenges()
                    badgeChallenge.badgeID = badgeId
                    badgeChallenge.challengeID = Challenges.objects.get(challengeID=assignToChallenges[j])
                    badgeChallenge.save()
                    print("Print the specific challenges: ")
                    print(str(badgeChallenge))
                        
            elif (str(assignChallenges) == '1'):
                # Save the badge-challenges relationships to the BadgeChallenges table
                allChallenges = Challenges.objects.all()
                for challenge in allChallenges:
                    badgeChallenge = BadgeChallenges()
                    badgeChallenge.badgeID = badgeId
                    badgeChallenge.challengeID = challenge
                    badgeChallenge.save()
                
    return redirect("/oneUp/badges/Badges")
    
