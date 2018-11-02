'''
Created on Oct 3, 2018

@author: Joel
'''
from django.shortcuts import redirect

from Instructors.views.utils import initialContextDict
from Students.models import Student, StudentRegisteredCourses, StudentProgressiveUnlocking
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Badges.models import ActionArguments, Rules, ProgressiveUnlocking, RuleEvents
from Badges.enums import Action, ObjectTypes, AwardFrequency
from Badges.conditions_util import get_events_for_condition,\
    stringAndPostDictToCondition

from django.contrib.auth.decorators import login_required
from Badges.systemVariables import logger

def DeleteProgressionRule(badge):
        
    # The next line deletes the conditions and everything else related to the rule
    badge.ruleID.delete_related()
    # Then we delete the rule itself
    badge.ruleID.delete()                 

@login_required
def createProgressiveUnlocking(request,obj,objType):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    # Thees will be pass as arguments
    context_dict,current_course = initialContextDict(request);
    
    if request.method == "POST": 
            # Check if creating a new badge or edit an exi sting one
            # If editing an existent one, we need to delete it first before saving the updated information in the database            
            if 'badgeId' in request.POST:   #edit or delete badge 
                badge = Badges.objects.get(pk=int(request.POST['badgeId']))
                oldRuleToDelete = badge.ruleID
            else:
                unlocking = ProgressiveUnlocking()  # create new unlocking rule  

                # Get unlocking info and the first condition
                name = request.POST['unlockingName'] # The entered Badge Name
                logger.debug("badge name: "+str(name))
                description = request.POST['unlockingDescript'] # The entered Badge Description
                logger.debug("badge description: "+str(description))
                    
                condition = stringAndPostDictToCondition(request.POST['cond-cond-string'],request.POST,current_course)
                logger.debug(condition)
                    
                # Save game rule to the Rules table
                gameRule = Rules()
                gameRule.conditionID = condition
                gameRule.actionID = Action.unlockedProgressive 
                gameRule.courseID = current_course
                
                awardFreq = int(request.POST['awardFrequency'])
                gameRule.awardFrequency = awardFreq
                print("CHOSEN OBJECT SPECIFIER STRING : "+request.POST['chosenObjectSpecifierString']);
                gameRule.objectSpecifier = request.POST['chosenObjectSpecifierString'];
                gameRule.save()
    
                # We get all of the related events.
                context = AwardFrequency.awardFrequency[awardFreq]['objectType']
                events = get_events_for_condition(condition,context)
                for event,isGlobal in events:
                    ruleEvent = RuleEvents()
                    ruleEvent.rule = gameRule
                    ruleEvent.event = event
                    ruleEvent.inGlobalContext = isGlobal
                    ruleEvent.save()
    
                # Save progressive unlocking object to db
                unlocking.ruleID = gameRule            
                unlocking.courseID = current_course
                unlocking.name = name
                unlocking.description = description
                unlocking.objectID = obj.pk
                if(objType == "challenge"):
                    unlocking.objectType = ObjectTypes.challenge
                elif(objType == "activity"):
                    unlocking.objectType = ObjectTypes.activity
                unlocking.save()
                
                if not (ActionArguments.objects.filter(ruleID = gameRule, sequenceNumber = 1, argumentValue=str(unlocking.pk)).exists()):
                    # Save the action 'unlocking progressively' to the ActionArguments Table
                    actionArgument = ActionArguments()
                    actionArgument.ruleID = gameRule
                    actionArgument.sequenceNumber = 1
                    actionArgument.argumentValue =  unlocking.pk
                    actionArgument.save()
                
                # Make Student objects for the pUnlocking Rule
                studentsInCourse = StudentRegisteredCourses.objects.filter(courseID=current_course)
                for sCourse in studentsInCourse:
                    student = sCourse.studentID
                    studentPUnlocking =  StudentProgressiveUnlocking()
                    studentPUnlocking.studentID = student
                    studentPUnlocking.pUnlockingRuleID = unlocking
                    studentPUnlocking.objectID = obj.pk
                    if(objType == "challenge"):
                        studentPUnlocking.objectType = ObjectTypes.challenge
                    elif(objType == "activity"):
                        studentPUnlocking.objectType = ObjectTypes.activity
                    studentPUnlocking.save()


                # if 'badgeId' in request.POST:
                #     oldRuleToDelete.delete_related()
                #     oldRuleToDelete.delete()  
                            
            # else:
            #     print("other")
            #     badge.ruleID.delete_related()
            #     badge.ruleID.delete()
            #     badge.delete()

    return True
    
