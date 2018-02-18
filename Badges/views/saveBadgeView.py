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
from Badges.enums import Action, Event, OperandTypes
from Badges.systemVariables import SystemVariable
from Badges.conditions_util import get_events_for_system_variable, get_events_for_condition,\
    cond_from_mandatory_cond_list, stringAndPostDictToCondition

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
            
def DetermineEvent(conditionOperandValue):
    # Note: This should be effectively removed soon and also can break for certain inputs.
    return get_events_for_system_variable(conditionOperandValue)[0]

@login_required
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
                
            badgeCondition = stringAndPostDictToCondition(request.POST['cond-cond-string'],request.POST,currentCourse)
            print(badgeCondition)
                
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
            badgeInformation.assignToChallenges = 1  # TODO: delete this field from the model
            badgeInformation.save()
            
            badgeId = badgeInformation
            print("badge id: "+str(badgeId.badgeID))
            if not (ActionArguments.objects.filter(ruleID = gameRule, sequenceNumber = 1, argumentValue=str(badgeId.badgeID)).exists()):
                # Save the action 'Giving a Badge' to the ActionArguments Table
                actionArgument = ActionArguments()
                actionArgument.ruleID = gameRule
                actionArgument.sequenceNumber = 1
                actionArgument.argumentValue =  badgeId.badgeID
                actionArgument.save()
                

                
    return redirect("/oneUp/badges/Badges")
    
