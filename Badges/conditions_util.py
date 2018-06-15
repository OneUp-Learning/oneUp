'''
Created on Jan 27, 2017

@author: kirwin
'''

from Badges.enums import OperandTypes, ObjectTypes, system_variable_type_to_HTML_type
from Badges.models import Conditions, FloatConstants, StringConstants, Dates, ConditionSet, ChallengeSet, ActivitySet, ActivityCategorySet,\
    TopicSet
from Instructors.models import Activities,ActivitiesCategory, Challenges, CoursesTopics
from Instructors.constants import unassigned_problems_challenge_name
from Badges.systemVariables import SystemVariable
from Badges.events import operandSetTypeToObjectType

#Determine the appropriate event type for each System Variable
def get_events_for_system_variable(var,context):
    # It may come in as a string rather than a number
    # This way we're sure we've got a number.
    var = int(var)
    # Then we just use it to find the systemVariable enum and we've added a field to this which is a list of events.
    return set(SystemVariable.systemVariables[var]['eventsWhichCanChangeThis'][context])

leaf_condition_operators = ['==','=','<','>','<=','>=','!=']
binary_condition_operators = ['AND','OR','NOT']
unary_condition_operators = ['NOT']
for_list_condition_operators = ['FOR_ALL','FOR_ANY']
def get_events_for_condition(cond, context):
    
    def getEventsFromConditionSet(condition,context):
        subConds = [condset.conditionInSet for condset in ConditionSet.objects.filter(parentCondition=condition)]
        eventSet = set()
        for subCond in subConds:
            eventSet = eventSet.union(get_events_for_condition(subCond,context))
        return eventSet
    
    if cond.operation in leaf_condition_operators:
        eventSet = set()
        if (cond.operand1Type == OperandTypes.systemVariable):
            eventSet = eventSet.union(get_events_for_system_variable(cond.operand1Value))
        if (cond.operand2Type == OperandTypes.systemVariable):
            eventSet = eventSet.union(get_events_for_system_variable(cond.operand2Value))
        return eventSet
    elif cond.operation in binary_condition_operators:
        if cond.operand1Type == OperandTypes.conditionSet:
            return getEventsFromConditionSet(cond)
        else:
            cond1events = get_events_for_condition(Conditions.objects.get(pk=cond.operand1Value),context)
            cond2events = get_events_for_condition(Conditions.objects.get(pk=cond.operand2Value),context)
            return cond1events.union(cond2events)
    elif cond.operation in unary_condition_operators:
        return get_events_for_condition(Conditions.objects.get(pk=cond.operand1Value), context)
    elif cond.operation in for_list_condition_operators:
        return get_events_for_condition(Conditions.objects.get(pk=cond.operand2Value), operandSetTypeToObjectType(cond.operand1Type))
    else:
        return "ERROR: Invalid operator in condition.  Should be one of '==','<','>','<=','>=','!=','AND','OR','NOT','FOR_ALL','FOR_ANY'."

letter_to_operation = {
    'D':'AND',
    'O':'OR',
}
def stringAndPostDictToCondition(conditionString,post,courseID):
    numRHSvalues = int(post["cond-atom-count"])
    rhsValueTable = {}
    for i in range(0,numRHSvalues):
        key = "cond-rhs-value"+str(i)
        if (key in post):
            rhsValueTable[i] = post[key]
        else:
            rhsValueTable[i] = False
            
    condTable = conditionString.split(";")
    mainCondIndex = int(condTable[0])
    
    def stringToCondHelper(string):
        if string[0]=='E': # empty.  Only used in special circumstances.  Should not appear in a well-formed condition
            return None
        elif string[0]=='A': # atom.  A single condition
            parts = string.split(".")
            cond = Conditions()
            cond.courseID = courseID
            cond.operation = parts[2]
            cond.operand1Type = OperandTypes.systemVariable
            cond.operand1Value = int(parts[1])
            value = int(parts[4])
            if parts[3] == "V":
                cond.operand2Type = OperandTypes.systemVariable
                cond.operand2Value = value
            elif parts[3] == "T":
                cond.operand2Type = OperandTypes.stringConstant
                stconst = StringConstants()
                stconst.stringValue = rhsValueTable[value]
                stconst.save()
                cond.operand2Value = stconst.stringID
            elif parts[3] == "N":
                cond.operand2Type = OperandTypes.immediateInteger
                cond.operand2Value = rhsValueTable[value]
            elif parts[3] == "X":
                cond.operand2Type = OperandTypes.boolean
                if rhsValueTable[value] == "false":
                    cond.operand2Value = 0
                else:
                    cond.operand2Value = 1
            elif parts[3] == "Y":
                cond.operand2Type = OperandTypes.dateConstant
                dconst = Dates()
                dconst.dateValue = rhsValueTable[value]
                dconst.save()
                cond.operand2Value = dconst.dateID
            cond.save()
            return cond
        elif string[0] == "D" or string[0] == "O": # AND or OR
            print("string="+string)
            subCondIndexList = string[3:-2].split(",")
            cond = Conditions()
            cond.courseID = courseID
            cond.operation = letter_to_operation[string[0]]
            cond.operand1Type = OperandTypes.conditionSet
            cond.operand1Value = 0
            cond.operand2Type = OperandTypes.noOperand
            cond.operand2Value = 0
            cond.save()
            
            for subCondIndex in subCondIndexList:
                subCondition = stringToCondHelper(condTable[int(subCondIndex)])
                if subCondition is not None:
                    condSetEntry = ConditionSet()
                    condSetEntry.parentCondition = cond
                    condSetEntry.conditionInSet = subCondition
                    condSetEntry.save()
            
            return cond
        elif string[0] == "F":
            print("for starting")
            cond = Conditions()
            cond.courseID = courseID
            if string[2] == "*":
                cond.operation = "FOR_ALL"
            elif string[2] == "1":
                cond.operation = "FOR_ANY"
            else:
                print("Not for all or for any")
                return None
            parts = string[3:].split(".")
            if parts[1] == "activity":
                cond.operand1Type = OperandTypes.activitySet
            elif parts[1] == "challenge":
                cond.operand1Type = OperandTypes.challengeSet
            elif parts[1] == "topic":
                cond.operand1Type = OperandTypes.topicSet
            elif parts[1] == "category":
                cond.operand1Type = OperandTypes.activtiyCategorySet   
            else:
                print("not activities, category, challenges, or topics, instead: "+parts[1])
                return None
            subCond = condTable[int(parts[3])]
            if subCond is None:
                print ("subCond is None. Val="+parts[3])
                return None
            else:
                cond.operand2Type = OperandTypes.condition
                cond.operand2Value = int(stringToCondHelper(subCond).conditionID)
            if parts[2] == "*":
                cond.operand1Value = 0
                cond.save()
            else:
                cond.operand1Value = 1
                cond.save()
                subThingieIndexList = parts[2][1:-2].split(",")
                if cond.operand1Type == OperandTypes.activitySet:
                    for activity in subThingieIndexList:
                        activitySetItem = ActivitySet()
                        activitySetItem.activity_id = int(activity)
                        activitySetItem.condition = cond
                        activitySetItem.save()
                elif cond.operand1Type == OperandTypes.challengeSet:
                    for challenge in subThingieIndexList:
                        challengeSetItem = ChallengeSet()
                        challengeSetItem.challenge_id = int(challenge)
                        challengeSetItem.condition = cond
                        challengeSetItem.save()
                elif cond.operand1Type == OperandTypes.topicSet:
                    for topic in subThingieIndexList:
                        topicSetItem = TopicSet()
                        topicSetItem.topic_id = int(topic)
                        topicSetItem.condition = cond
                        topicSetItem.save()
                elif cond.operand1Type == OperandTypes.activtiyCategorySet:
                    for activityCategory in subThingieIndexList:
                        activityCategorySetItem = ActivityCategorySet()
                        activityCategorySetItem.category_id= int(activityCategory)
                        activityCategorySetItem.condition = cond
                        activityCategorySetItem.save()
                else:
                    print("for leaving at the return which should never happen")
                    return None
            print("for completed")
            return cond;
        else:
            return None
        
    return stringToCondHelper(condTable[mainCondIndex])

# The following only covers operand types which can occur in atoms
operand_types_to_char = {
    OperandTypes.systemVariable:"V",
    OperandTypes.boolean:"X",
    OperandTypes.dateConstant:"Y",
    OperandTypes.immediateInteger:"N",
    OperandTypes.stringConstant:"T",
}
def databaseConditionToJSONString(condition):
    def handleAtom():
        output = '{"type":"ATOM","op":"'+condition.operation+'","lhs":"'
        if condition.operand1Type != OperandTypes.systemVariable: # We have a problem because this should always be true for atoms when using our condition engine.
            return "";
        else: # No problem
            output += str(condition.operand1Value)+'","rhstype":"'
        if condition.operand2Type == OperandTypes.systemVariable:
            output += 'V","rhsvalue":"'+str(condition.operand2Value)+'"}'
        elif condition.operand2Type == OperandTypes.boolean:
            output += 'X","rhsvalue":"'+str(condition.operand2Value==1)+'"}'
        elif condition.operand2Type == OperandTypes.immediateInteger:
            output += 'N","rhsvalue":"'+str(condition.operand2Value)+'"}'
        elif condition.operand2Value == OperandTypes.dateConstant:
            output += 'Y","rhsvalue":"'+str(Dates.objects.get(pk=condition.operand2Value).dateValue)+'"}'
        elif condition.operand2Value == OperandTypes.stringConstant:
            output += 'T","rhsvalue":"'+StringConstants.objects.get(pk=condition.operand2Value).stringValue+'"}'
        else: # Other types should not appear as the right hand side of an atom.
            return "" 
        return output
    def handleAndOr():
        output = '{"type":"'+condition.operation+'","subConds":['
        if condition.operand1Type == OperandTypes.conditionSet:
            subConds = [condSet.conditionInSet for condSet in ConditionSet.objects.filter(parentCondition = condition)]
        else: # old-style AND or OR of just two conditions.  This is being phased out, but is still supported here 
            subConds = [Conditions.objects.get(pk=condition.operand1Value),Conditions.objects.get(pk=condition.operand2Value)]
        for subCond in subConds:
            output += databaseConditionToJSONString(subCond)+","
        output += ']}'
        return output
    def handleFor():
        output = '{"type":"FOR","allOrAny":"'+condition.operation[4:]+'","allObjects":"'+str(condition.operand1Value == 0)+'","objectType":"'
        if condition.operand1Type == OperandTypes.activitySet:
            output += 'activity","objects":['
            activityIDs = [actSet.activity.activityID for actSet in ActivitySet.objects.filter(condition=condition)]
            for activityID in activityIDs:
                output += '"'+str(activityID)+'",'
        elif condition.operand1Type == OperandTypes.challengeSet:
            output += 'challenge","objects":['
            challengeIDs = [challSet.challenge.challengeID for challSet in ChallengeSet.objects.filter(condition=condition)]
            for challengeID in challengeIDs:
                output += '"'+str(challengeID)+'",'
        elif condition.operand1Type == OperandTypes.topicSet:
            output += 'topic","objects":['
            topicsIDs = [topicSet.topic.topicID for topicSet in TopicSet.objects.filter(condition=condition)]
            for topicID in topicsIDs:
                output += '"'+str(topicID)+'",'
        elif condition.operand1Type == OperandTypes.activtiyCategorySet:
            output += 'category","objects":['
            activityCategoryIDs = [activityCategorySet.category.categoryID for activityCategorySet in ActivityCategorySet.objects.filter(condition=condition)]
            for activityCategoryID in activityCategoryIDs:
                output += '"'+str(activityCategoryID)+'",'
        else: # Other types not supported in FOR_ALL or FOR_ANY conditions.
            return ""
        # In the next statement, we presuppose that the type of the second operand is a condition because it is supposed to be
        output += '],"subCond":'+databaseConditionToJSONString(Conditions.objects.get(pk=condition.operand2Value)) +"}"
        return output
    
    operationToFunctionTable = {
        "=":handleAtom,
        ">":handleAtom,
        "!=":handleAtom,
        ">=":handleAtom,
        "<=":handleAtom,
        "<":handleAtom,
        "AND":handleAndOr,
        "OR":handleAndOr,
        "FOR_ALL":handleFor,
        "FOR_ANY":handleFor,
    }
    return operationToFunctionTable[condition.operation]()

def setUpContextDictForConditions(context_dict,course):
    var_list = []    
    for sysVarIndex in SystemVariable.systemVariables.keys():
        sysVarTable = SystemVariable.systemVariables[sysVarIndex]
        sysVar = {
            "id":sysVarIndex,
            "name":sysVarTable["displayName"],
            "tooltip":sysVarTable["description"],
            "type":system_variable_type_to_HTML_type[sysVarTable["type"]],
            "objects":[ObjectTypes.objectTypes[x] for x in sysVarTable["functions"].keys()],
        }
        var_list.append(sysVar)
    context_dict['variables'] = var_list

    chall_list = [{"id":ch.challengeID,"name":ch.challengeName} for ch in Challenges.objects.filter(courseID = course).exclude(challengeName=unassigned_problems_challenge_name)]
    act_list = [{"id":act.activityID,"name":act.activityName} for act in Activities.objects.filter(courseID = course)]
    actCat_list = [{"id":actCat.categoryID,"name":actCat.name} for actCat in ActivitiesCategory.objects.filter(courseID = course)]
    topic_list = [{"id":ct.topicID.topicID,"name":ct.topicID.topicName} for ct in CoursesTopics.objects.filter(courseID = course)]
    
    
    context_dict['objectTypes'] = [{"name":"challenge","plural":"challenges","objects":chall_list },
                                   {"name":"activity","plural":"activities", "objects":act_list},
                                   {"name":"topic","plural":"topics","objects":topic_list},
                                   {"name":"category","plural":"categories","objects":actCat_list},]
    context_dict['defaultObject'] = "challenge"
    return context_dict