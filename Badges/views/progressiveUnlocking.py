'''
Created on Oct 3, 2018

@author: Joel
'''
from django.shortcuts import redirect, render

from Instructors.views.utils import initialContextDict
from Instructors.models import Challenges, Activities, CoursesTopics, ActivitiesCategory
from Students.models import Student, StudentRegisteredCourses, StudentProgressiveUnlocking
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Badges.models import ActionArguments, Rules, ProgressiveUnlocking, RuleEvents
from Badges.enums import Action, ObjectTypes, AwardFrequency
from Badges.conditions_util import get_events_for_condition,\
    stringAndPostDictToCondition

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Badges.systemVariables import logger
               
def ProgressiveUnlockingRules(request):
    
    context_dict,current_course = initialContextDict(request)
    # Returns the page for editing a rule         
    if request.GET:   
        if 'editRule' in request.GET and  request.GET['editRule'] == "True":
            print("we want to edit the rule")
            #return editRule(request,current_course,context_dict)
            return createRule(request,current_course,context_dict)


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
        print("####")
        print(objectString)
        if objectString == 'activity':
            objs.append({'rule': rule, 'type' : 'Activity', 'typeString': 'activity'})
        elif objectString == 'challenge':
            chall_list = Challenges.objects.filter(pk=rule.objectID)
            if len(chall_list == 1):
                chall = chall_list[0]
                if(chall.isGraded): # It is a serious chall
                    objs.append({'rule': rule, 'type' : 'Serious Challenge','typeString': 'challenge'})
                else:
                    objs.append({'rule': rule, 'type' : 'WarmUp Challenge','typeString': 'challenge'})
            else:
                print("We have a progressive unlocking rule for a challenge which has since been deleted")
                rule.delete()
        elif objectString == 'topic':
            objs.append({'rule': rule, 'type' : 'Topic','typeString': "topic"})
        elif objectString == 'activityCategory':
            print("hi")
            objs.append({'rule': rule, 'type' : 'Activity Category','typeString': "activityCategory"})


    context_dict['rules'] = zip(range(1,len(objs)+1), objs) # had to zip this in order to make the tool tip work

    # Code for selector
    objTypes.append( {'id' : ObjectTypes.activity, 'string' : 'Activity'} ) 
    objTypes.append( {'id' : ObjectTypes.challenge, 'string' : ' Challenge' } )
    objTypes.append( {'id' : ObjectTypes.topic, 'string' : 'Topic' } )
    objTypes.append( {'id' : ObjectTypes.activityCategory, 'string' : 'Activity Category' } )
    context_dict['filter'] = objTypes
    context_dict['currentFilter'] = int(ruleType)

    return render(request,'Badges/progressiveUnlocking.html', context_dict)

def createRule(request,current_course,context_dict):
    print("we want to make a new rule")
    if request.GET: 
        if 'editRule' in request.GET and request.GET['editRule'] == "True":
            print("Edit")
            pk = request.GET['ruleID']
            rule = ProgressiveUnlocking.objects.filter(pk=pk).first()
            
            print(rule.name)
            context_dict['pRule'] = rule
            context_dict = setUpContextDictForConditions(context_dict,current_course,rule.ruleID)
            
            objectString =  ObjectTypes.objectTypes[rule.objectType]
        
            context_dict['edit'] = True
            if objectString == 'activity':
                context_dict['type'] = {'id' : ObjectTypes.activity, 'string' : 'Activity'}
            elif objectString == 'challenge':
                chall = Challenges.objects.get(pk=rule.objectID)
                if(chall.isGraded): # It is a serious chall
                    context_dict['type']={'id' : ObjectTypes.challenge, 'string' : ' Serious Challenge' }
                else:
                    context_dict['type'] = {'id' : ObjectTypes.challenge, 'string' : ' WarmUp Challenge' }
            elif objectString == 'topic':
                context_dict['type'] = {'id' : ObjectTypes.topic, 'string' : 'Topic' }
            elif objectString == 'activityCategory':
                context_dict['type'] = {'id' : ObjectTypes.activityCategory, 'string' : 'ActivityCategory' }

        else:
            context_dict = setUpContextDictForConditions(context_dict,current_course,None)

        # Code for the object selector
        if 'ruleType' in request.GET:
            if request.GET['ruleType'] == 'challenge':
                ruleType = ObjectTypes.challenge
                if 'warmUp' in request.GET and request.GET['warmUp'] == 'True':
                    objs = Challenges.objects.filter(courseID = current_course,isGraded=False)
                    context_dict['ruleTypeString'] = ' WarmUp Challenge'
                else:
                    objs = Challenges.objects.filter(courseID = current_course,isGraded=True)
                    context_dict['ruleTypeString'] = ' Serious Challenge'

            elif request.GET['ruleType'] == 'activity':
                ruleType = ObjectTypes.activity
                objs = Activities.objects.filter(courseID=current_course)
                context_dict['ruleTypeString'] = 'Activity'
                
            
            elif request.GET['ruleType'] == 'topic':
                ruleType = ObjectTypes.topic
                objs = CoursesTopics.objects.filter(courseID=current_course)
                context_dict['ruleTypeString'] = 'Topic'
            
            elif request.GET['ruleType'] == 'activityCategory':
                print("######## CATS")
                ruleType = ObjectTypes.activityCategory
                objs = ActivitiesCategory.objects.filter(courseID=current_course)
                context_dict['ruleTypeString'] = 'Activity Category'

            context_dict['ruleType'] = ruleType
            context_dict['objs'] = objs
        
        # Code for object type selector
        objTypes = []
        objTypes.append( {'id' : ObjectTypes.activity, 'string' : 'Activity'} ) 
        objTypes.append( {'id' : ObjectTypes.challenge, 'string' : ' WarmUp Challenge' } )
        objTypes.append( {'id' : ObjectTypes.challenge, 'string' : ' Serious Challenge' } )
        objTypes.append( {'id' : ObjectTypes.topic, 'string' : 'Topic' } )
        objTypes.append( {'id' : ObjectTypes.activityCategory, 'string' : 'ActivityCategory' } )
        context_dict['filter'] = objTypes
    
        return render(request, 'Badges/AddProgressiveUnlocking.html', context_dict)
        

    if request.POST:
        print("We are in post for making a rule")
        
        if 'editRule' in request.POST:
            pk = request.POST['editRule']
            unlocking = ProgressiveUnlocking.objects.filter(pk=pk).first()
            unlocking.ruleID.delete()
        else:
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
        oType = request.POST['ruleObjectType']
        if oType == 'Activity':
            unlocking.objectType = ObjectTypes.activity
        elif oType == 'WarmUp' or oType == 'Serious':
            unlocking.objectType = ObjectTypes.challenge
        elif oType == 'Topic':
            unlocking.objectType = ObjectTypes.topic
        elif oType == 'ActivityCategory':
            unlocking.objectType = ObjectTypes.activityCategory
        unlocking.save()
        
        if not (ActionArguments.objects.filter(ruleID = gameRule, sequenceNumber = 1, argumentValue=str(unlocking.pk)).exists()):
            # Save the action 'unlocking progressively' to the ActionArguments Table
            actionArgument = ActionArguments()
            actionArgument.ruleID = gameRule
            actionArgument.sequenceNumber = 1
            actionArgument.argumentValue =  unlocking.pk
            actionArgument.save()
        
        if 'editRule' in request.POST:
            sRules = StudentProgressiveUnlocking.objects.filter(courseID=current_course,pUnlockingRuleID=pk)
            for studentRule in sRules:
                studentRule.pUnlockingRuleID = unlocking
                studentRule.objectID = request.POST['ruleTargetObject']
                if oType == 'Activity':
                    studentRule.objectType = ObjectTypes.activity
                elif oType == 'WarmUp' or oType == 'Serious':
                    studentRule.objectType = ObjectTypes.challenge
                elif oType == 'Topic':
                    studentRule.objectType = ObjectTypes.topic
                elif oType == 'ActivityCategory':
                    studentRule.objectType = ObjectTypes.activityCategory
                studentRule.save()
        else:
            # Make Student objects for the pUnlocking Rule
            studentsInCourse = StudentRegisteredCourses.objects.filter(courseID=current_course)
            for sCourse in studentsInCourse:
                student = sCourse.studentID
                studentPUnlocking =  StudentProgressiveUnlocking()
                studentPUnlocking.studentID = student
                studentPUnlocking.pUnlockingRuleID = unlocking
                studentPUnlocking.courseID = current_course
                studentPUnlocking.objectID = request.POST['ruleTargetObject']
                if oType == 'Activity':
                    studentPUnlocking.objectType = ObjectTypes.activity
                elif oType == 'WarmUp' or oType == 'Serious':
                    studentPUnlocking.objectType = ObjectTypes.challenge
                elif oType == 'Topic':
                    studentPUnlocking.objectType = ObjectTypes.topic
                elif oType == 'ActivityCategory':
                    studentPUnlocking.objectType = ObjectTypes.activityCategory
                studentPUnlocking.save()
        
    return redirect('/oneUp/badges/ProgressiveUnlocking') #(request,'Badges/progressiveUnlocking.html', context_dict)

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

def getObjs(request):
    context_dict,current_course = initialContextDict(request)
    objs = {'objs': []}

    if 'typeIndex' in request.POST:
        if request.POST['typeIndex'] == 'WarmUp':
             challs = Challenges.objects.filter(courseID = current_course,isGraded=False)
             for c in challs:
                 objs['objs'].append({'id': c.pk, 'name': c.challengeName})

        elif request.POST['typeIndex'] == 'Serious':
            challs = Challenges.objects.filter(courseID = current_course,isGraded=True)
            for c in challs:
                 objs['objs'].append({'id': c.pk, 'name': c.challengeName})

        elif request.POST['typeIndex'] == 'Activity':
            acts = Activities.objects.filter(courseID=current_course)
            for a in acts:
                objs['objs'].append({'id': a.pk, 'name': a.activityName})

        elif request.POST['typeIndex'] == 'Topic':
                topics = CoursesTopics.objects.filter(courseID=current_course)
                for t in topics:
                    objs['objs'].append({'id': t.pk, 'name': t.topicID.topicName})
        
        elif request.POST['typeIndex'] == 'ActivityCategory':
                actCats = ActivitiesCategory.objects.filter(courseID=current_course)
                for cat in actCats:
                    objs['objs'].append({'id': cat.pk, 'name': cat.name})

    return JsonResponse(objs)
