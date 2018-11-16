'''
Created on Oct 3, 2018

@author: Joel
'''
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict
from Instructors.models import Challenges, Activities
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

def ProgressiveUnlockingRules(request):
    
    context_dict,current_course = initialContextDict(request)
    # Returns the page for editing a rule         
    if request.GET:   
        if 'editRule' in request.GET and  request.GET['editRule'] == "True":
            print("we want to edit the rule")
            editRule(request)

        elif 'delete' in request.GET and request.GET['delete'] == "True":
            print("we want to delete the rule")
            deleteRule(request,current_course,context_dict)

        # Preps webpage for making a rule. The actual function that makes it is below
        elif 'create' in request.GET and request.GET['create'] == "True":
            return createRule(request,current_course,context_dict)
    
    # Code for when making a rule
    elif request.POST:
        print("We are in post")
        if 'whatWeAreDoing' in request.POST:
            if request.POST['whatWeAreDoing'] == 'create':
               return createRule(request,current_course,context_dict)
    
    return listRules(request,current_course,context_dict)



# Returns the code for displays the list view with all rules
def listRules(request,current_course,context_dict):
    # This handles filtering
    if 'objTypeFilter' in request.POST:
        ruleType = request.POST['objTypeFilter']
        if ruleType == 'all':
            rules = ProgressiveUnlocking.objects.filter(courseID = current_course)
            ruleType = 1
        else:
            rules = ProgressiveUnlocking.objects.filter(courseID = current_course,objectType=ruleType)
    else:
        rules = ProgressiveUnlocking.objects.filter(courseID = current_course)
        ruleType = 1
    
    objs = [] # have to covert rule ints into strings for front end
    objTypes = []

    for rule in rules:
        objectString =  ObjectTypes.objectTypes[rule.objectType]
        if objectString == 'activity':
            objs.append({'rule': rule, 'type' : 'Activity'})
        elif objectString == 'challenge':
            objs.append({'rule': rule, 'type' : 'Challenge'})

    context_dict['rules'] = objs

    # Code for selector
    objTypes.append( {'id' : ObjectTypes.activity, 'string' : 'Activity'} ) 
    objTypes.append( {'id' : ObjectTypes.challenge, 'string' : 'Challenge' } )
    context_dict['filter'] = objTypes
    context_dict['currentFilter'] = int(ruleType)

    return render(request,'Badges/progressiveUnlocking.html', context_dict)

def createRule(request,current_course,context_dict):
    print("we want to make a new rule")
    if request.GET:
        context_dict = setUpContextDictForConditions(context_dict,current_course,None)
        
        if 'ruleType' in request.GET:
            if request.GET['ruleType'] == 'challenge':
                ruleType = ObjectTypes.challenge
                if 'warmUp' in request.GET and request.GET['warmUp'] == 'True':
                    objs = Challenges.objects.filter(courseID = current_course,isGraded=False)
                else:
                    objs = Challenges.objects.filter(courseID = current_course,isGraded=True)

            elif request.GET['ruleType'] == 'activity':
                ruleType = ObjectTypes.activity
                objs = Activities.objects.filter(courseID=current_course)

            context_dict['ruleType'] = ruleType
            context_dict['objs'] = objs

            return render(request, 'Badges/AddProgressiveUnlocking.html', context_dict)

    if request.POST:
        print("We are in post for making a rule")
        print(request.POST)
        unlocking = ProgressiveUnlocking()  # create new unlocking rule  

        # Get unlocking info and the first condition
        name = request.POST['unlockingName'] # The entered Badge Name
        logger.debug("Rule name: "+str(name))
        description = request.POST['unlockingDescript'] # The entered Badge Description
        logger.debug("P Unlocking Rule description: "+str(description))
            
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
        unlocking.objectID = request.POST['ruleTargetObject']
        unlocking.objectType = request.POST['ruleObjectType']
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
            studentPUnlocking.courseID = current_course
            studentPUnlocking.objectID = request.POST['ruleTargetObject']
            studentPUnlocking.objectType = request.POST['ruleObjectType']
            studentPUnlocking.save()
        
    return redirect('/oneUp/badges/ProgressiveUnlocking') #(request,'Badges/progressiveUnlocking.html', context_dict)

def editRule():
    pass

def deleteRule(request,current_course,context_dict):
    if "ruleID" in request.GET:
        rID = request.GET['ruleID']
        try:
            rule = ProgressiveUnlocking.objects.get(pk=rID)
            rule.ruleID.delete_related()
            rule.ruleID.delete()
            rule.delete()   
        except:
            logger.debug("Rule was not found when trying to delete")
    else:
        logger.debug("Nothing to delete no id found") 

    return redirect('/oneUp/badges/ProgressiveUnlocking')    