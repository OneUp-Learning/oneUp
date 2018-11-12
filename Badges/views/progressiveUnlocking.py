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
    #Returns the page for editing a rule         
    if request.GET:   
        if 'editRule' in request.GET and  request.GET['editRule'] == "True":
            print("we want to edit the rule")
            editRule(request)

        elif 'delete' in request.GET and request.GET['delete'] == "True":
            print("we want to delete the rule")
            deleteRule(request)

        # Preps webpage for making a rule. The actual function that makes it is below
        elif 'create' in request.GET and request.GET['create'] == "True":
            return createRule(request,current_course,context_dict)
    
    # Code for when making a rule
    elif request.POST:
        print("We are in post")
        print(request.POST)
        if 'whatWeAreDoing' in request.POST:
            if request.POST['whatWeAreDoing'] == 'create':
               return createRule(request,current_course,context_dict)
    
    return listRules(request,current_course,context_dict)



# Returns the code for displays the list view with all rules
def listRules(request,current_course,context_dict):
    rules = ProgressiveUnlocking.objects.filter(courseID = current_course)
    objs = [] # have to covert rule ints into strings for front end

    for rule in rules:
        objectString =  ObjectTypes.objectTypes[rule.objectType]
        objs.append({'rule': rule, 'type' : objectString})

    context_dict['rules'] = objs
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

def deleteRule():
    pass

def filterRules():
    pass


@login_required
def createProgressiveUnlocking(request):#,obj,objType):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    # Thees will be pass as arguments
    context_dict,current_course = initialContextDict(request);

    # TODO add a checker to see if the person is a instructor
    
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
                    studentPUnlocking.courseID = current_course
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
    elif request.method == "GET":

        #Returns the page for editing a rule            
        if request.GET['edit'] == "True":
            print("we want to edit the rule")


        elif request.GET['delete'] == "True":
            print("we want to delete the rule")
        
        elif request.GET['create'] == "True":
            print("we want to make a new rule")
    
        # Returns the code for displays the list view with all rules
        else:
            rules = ProgressiveUnlocking.objects.filter(courseID = current_course)
            objs = [] # have to covert rule ints into strings for front end

            for rule in rules:
                objectString =  ObjectTypes.objectTypes[rule.objectType]
                objs.append({'rule': rule, 'type' : objectString})

            context_dict['rules'] = objs
            return render(request,'Badges/progressiveUnlocking.html', context_dict)
        
    return render(request,'Badges/progressiveUnlocking.html', context_dict)
