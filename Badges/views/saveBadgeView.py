'''
Created on Nov 3, 2014
Last updated Dec 21, 2016

@author: Swapna
'''
from django.shortcuts import redirect

from Instructors.views.utils import initialContextDict
from Badges.models import ActionArguments, Rules, Badges, RuleEvents, BadgesInfo
from Badges.enums import Action, ObjectTypes, AwardFrequency
from Badges.conditions_util import get_events_for_condition,\
    stringAndPostDictToCondition

from django.contrib.auth.decorators import login_required
from Badges.systemVariables import logger

def DeleteBadgeRule(badge):
        
    # The next line deletes the conditions and everything else related to the rule
    badge.ruleID.delete_related()
    # Then we delete the rule itself
    badge.ruleID.delete()                 

@login_required
def SaveBadge(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,current_course = initialContextDict(request);
    
    if request.method == "POST": 

        if 'isManualBadge' in request.POST:
            # Check if creating a new badge or edit an existing one
            # If editing an existent one, we need to delete it first before saving the updated information in the database            
                if 'badgeId' in request.POST:   #edit or delete badge 
                    badge = BadgesInfo.objects.get(pk=int(request.POST['badgeId']))
                                            
                else:
                    badge = BadgesInfo()  # create new badge             
                if 'edit' in request.POST:
                # Get badge info and the first condition
                    badgeName = request.POST['badgeName'] # The entered Badge Name
                    badgeImage = request.POST['badgeImage'] # The Chosen Badge Image Name
                    badgeDescription = request.POST['badgeDescription'] # The entered Badge Description

                    # Save badge information to the Badges Table
                    badge.courseID = current_course
                    badge.badgeName = badgeName
                    badge.badgeDescription = badgeDescription
                    badge.badgeImage = badgeImage
                    badge.manual = True;
                    badge.save()
                else:
                    print("manualBadge")
                    badge.delete()
            
        else:
            
            # Check if creating a new badge or edit an existing one
            # If editing an existent one, we need to delete it first before saving the updated information in the database            
            if 'badgeId' in request.POST:   #edit or delete badge 
                badge = Badges.objects.get(pk=int(request.POST['badgeId']))
                oldRuleToDelete = badge.ruleID
            else:
                badge = Badges()  # create new badge             
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
                
                awardFreq = int(request.POST['awardFrequency'])
                gameRule.awardFrequency = awardFreq
                print("CHOSEN OBJECT SPECIFIER STRING : "+request.POST['chosenObjectSpecifierString']);
                gameRule.objectSpecifier = request.POST['chosenObjectSpecifierString'];
                gameRule.save()
    
                # We get all of the related events.
                context = AwardFrequency.awardFrequency[awardFreq]['objectType']
                events = get_events_for_condition(badgeCondition,context)
                for event,isGlobal in events:
                    ruleEvent = RuleEvents()
                    ruleEvent.rule = gameRule
                    ruleEvent.event = event
                    ruleEvent.inGlobalContext = isGlobal
                    ruleEvent.save()
    
                # Save badge information to the Badges Table
                badge.ruleID = gameRule            
                badge.courseID = current_course
                badge.badgeName = badgeName
                badge.badgeDescription = badgeDescription
                badge.badgeImage = badgeImage
                badge.manual = False;
                badge.save()
                
                badgeId = badge
                logger.debug("badge id: "+str(badgeId.badgeID))
                if not (ActionArguments.objects.filter(ruleID = gameRule, sequenceNumber = 1, argumentValue=str(badgeId.badgeID)).exists()):
                    # Save the action 'Giving a Badge' to the ActionArguments Table
                    actionArgument = ActionArguments()
                    actionArgument.ruleID = gameRule
                    actionArgument.sequenceNumber = 1
                    actionArgument.argumentValue =  badgeId.badgeID
                    actionArgument.save()
            if 'edit' in request.POST:
                oldRuleToDelete.delete_related()
                oldRuleToDelete.delete()  
                
            else:
                print("other")
                badge.delete()
                
    return redirect("/oneUp/badges/Badges")
    
