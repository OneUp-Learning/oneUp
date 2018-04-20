'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.shortcuts import redirect

from Instructors.views.utils import initialContextDict
from Badges.models import ActionArguments, Rules, Badges, RuleEvents
from Badges.enums import Action
from Badges.conditions_util import get_events_for_system_variable, get_events_for_condition,\
    stringAndPostDictToCondition

from django.contrib.auth.decorators import login_required
from Badges.systemVariables import logger

def DeleteBadgeRule(badge):
        
    # The next line deletes the conditions and everything else related to the rule
    badge.ruleID.delete_related()
    # Then we delete the rule itself
    badge.ruleID.delete()                 
            
def DetermineEvent(conditionOperandValue):
    # Note: This should be effectively removed soon and also can break for certain inputs.
    return get_events_for_system_variable(conditionOperandValue)[0]

@login_required
def SaveBadge(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,current_course = initialContextDict(request);
    
    if request.method == "POST": 

        # Check if creating a new badge or edit an existing one
        # If editing an existent one, we need to delete it first before saving the updated information in the database            
        if 'badgeId' in request.POST:   #edit or delete badge 
            logger.debug("Badge to Edit/Delete Id: "+str(request.POST['badgeId']))
            badgeInformation = Badges.objects.get(pk=int(request.POST['badgeId']))
            DeleteBadgeRule(badgeInformation)
        else:
            badgeInformation = Badges()  # create new badge
                        
        if 'edit' in request.POST:
            # Get badge info and the first condition
            badgeName = request.POST['badgeName'] # The entered Badge Name
            logger.debug("badge name: "+str(badgeName))
            badgeDescription = request.POST['badgeDescription'] # The entered Badge Description
            logger.debug("badge description: "+str(badgeDescription))
            badgeImage = request.POST['badgeImage'] # The Chosen Badge Image Name
            logger.debug("badge image: "+str(badgeImage))
                
            badgeCondition = stringAndPostDictToCondition(request.POST['cond-cond-string'],request.POST,current_course)
            logger.debug(badgeCondition)
                
            # Save game rule to the Rules table
            gameRule = Rules()
            gameRule.conditionID = badgeCondition
            gameRule.actionID = Action.giveBadge 
            gameRule.courseID = current_course
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
            badgeInformation.courseID = current_course
            badgeInformation.badgeName = badgeName
            badgeInformation.badgeDescription = badgeDescription
            badgeInformation.badgeImage = badgeImage
            badgeInformation.assignToChallenges = 1  # TODO: delete this field from the model
            badgeInformation.save()
            
            badgeId = badgeInformation
            logger.debug("badge id: "+str(badgeId.badgeID))
            if not (ActionArguments.objects.filter(ruleID = gameRule, sequenceNumber = 1, argumentValue=str(badgeId.badgeID)).exists()):
                # Save the action 'Giving a Badge' to the ActionArguments Table
                actionArgument = ActionArguments()
                actionArgument.ruleID = gameRule
                actionArgument.sequenceNumber = 1
                actionArgument.argumentValue =  badgeId.badgeID
                actionArgument.save()

        else:
            badgeInformation.delete()
                
    return redirect("/oneUp/badges/Badges")
    
