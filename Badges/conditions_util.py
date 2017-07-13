'''
Created on Jan 27, 2017

@author: kirwin
'''

from Badges.enums import SystemVariable, Event, OperandTypes
from Badges.models import Conditions, FloatConstants, StringConstants, Dates, ConditionSet, ChallengeSet, ActivitySet
from Instructors.models import Activities, Challenges

#Determine the appropriate event type for each System Variable
def get_events_for_system_variable(var):
    # It may come in as a string rather than a number
    # This way we're sure we've got a number.
    var = int(var)
    # Then we just use it to find the systemVariable enum and we've added a field to this which is a list of events.
    return SystemVariable.systemVariables[var]['eventsWhichCanChangeThis']

leaf_condition_operators = ['==','<','>','<=','>=','!=']
binary_condition_operators = ['AND','OR','NOT']
unary_condition_operators = ['NOT']
def get_events_for_condition(cond):
    if cond.operation in leaf_condition_operators:
        events = []
        if (cond.operand1Type == OperandTypes.systemVariable):
            events.extend(get_events_for_system_variable(cond.operand1Value))
        if (cond.operand2Type == OperandTypes.systemVariable):
            events.extend(get_events_for_system_variable(cond.operand2Value))
        return events
    elif cond.operation in binary_condition_operators:
        cond1events = get_events_for_condition(Conditions.objects.get(pk=cond.operand1Value))
        cond2events = get_events_for_condition(Conditions.objects.get(pk=cond.operand2Value))
        return cond1events + cond2events
    elif cond.operation in unary_condition_operators:
        return get_events_for_condition(Conditions.objects.get(pk=cond.operand1Value))
    else:
        return "ERROR: Invalid operator in condition.  Should be one of '==','<','>','<=','>=','!='."
    
# Given a condition which begins with a set of ANDs at the top, this breaks down everything
# joined by AND into a list.  If given a condition which does not start with ANDs at the top,
# it simply returns it.  If it encounters OR or NOT, these are treated like leaf nodes and
# returned as part of the list.
def get_mandatory_conditions(cond):
    if cond.operation == 'AND':
        mc1 = get_mandatory_conditions(Conditions.objects.get(pk=cond.operand1Value))
        mc2 = get_mandatory_conditions(Conditions.objects.get(pk=cond.operand2Value))
        return mc1+mc2
    else:
        return [cond]

# Assuming that we start out with a big subtree of conditions joined by ANDs (in any shape)
# this finds all the leafs of that subtree and returns it.
# Any conditions joined via OR or NOT are trimmed off.
def get_mandatory_conditions_without_or_and_not(cond):
    if cond.operation == 'AND':
        mc1 = get_mandatory_conditions(Conditions.objects.get(pk=cond.operand1Value))
        mc2 = get_mandatory_conditions(Conditions.objects.get(pk=cond.operand2Value))
        return mc1+mc2
    elif cond.operation in leaf_condition_operators:
        return [cond]
    

# This takes in a list of conditions (NOTE: method only saves Conditions objects it creates.
# saving all other Conditions objects it creates is up to the calling function) and
# builds a tree of AND conditions which include all of the listed conditions.  It then
# returns that condition.
def cond_from_mandatory_cond_list(cond_list):
    print("Calling mandatory_cond_list:"+str(cond_list))
    cond_count = len(cond_list)
    if cond_count == 0:
        return "Error.  At least one condition must be present."
    elif cond_count == 1:
        return cond_list[0]
    else:
        first_cond = cond_list[0]
        second_cond = cond_list[1]
        rest_conds = cond_list[2:]
        new_cond = Conditions()
        new_cond.operation = 'AND'
        new_cond.operand1Type = OperandTypes.condition
        new_cond.operand1Value = first_cond.conditionID
        new_cond.operand2Type = OperandTypes.condition
        new_cond.operand2Value = second_cond.conditionID
        new_cond.save()
        rest_conds.append(new_cond)
        return cond_from_mandatory_cond_list(rest_conds)    

# Given a condition we find the mandatory subcondition which says which challenge this is connected to.
# We assume for this that the condition will have an associated challenge somewhere in the initial
# subtree with all of the ANDs.
def get_associated_challenge_if_exists(cond):
    mand_conds = get_mandatory_conditions(cond)
    for mc in mand_conds:
        if (    mc.operand1Type == OperandTypes.systemVariable
                and mc.operand1Value == SystemVariable.challengeId
                and mc.operand2Type == OperandTypes.immediateInteger
        ):
            if Challenges.objects.filter(challengeID = mc.operand2Value).exists():
                return (True,mc.operand2Value)
        if (    mc.operand2Type == OperandTypes.systemVariable
                and mc.operand2Value == SystemVariable.challengeId
                and mc.operand2Type == OperandTypes.immediateInteger
        ):
            if Challenges.objects.filter(challengeID = mc.operand1Value).exists():
                return (True,mc.operand1Value)

    # We have finished the whole loop and found nothing/
    return (False,"No associated challenge found")
def get_associated_activity_if_exists(cond):
    mand_conds = get_mandatory_conditions(cond)
    for mc in mand_conds:
        if (    mc.operand1Type == OperandTypes.systemVariable
                and mc.operand1Value == SystemVariable.challengeId
                and mc.operand2Type == OperandTypes.immediateInteger
        ):
            if Activities.objects.filter(activityID = mc.operand2Value).exists():
                return (True,mc.operand2Value)
        if (    mc.operand2Type == OperandTypes.systemVariable
                and mc.operand2Value == SystemVariable.challengeId
                and mc.operand2Type == OperandTypes.immediateInteger
        ):
            if Activities.objects.filter(activityID = mc.operand1Value).exists():
                return (True,mc.operand1Value)

    # We have finished the whole loop and found nothing/
    return (False,"No associated challenge found")
# Takes a list of conditions and removes any which associate with a challenge
def filter_out_associated_challenges(cond_list):

    # Utility function for identifying conditions which are restrictions on which challenges
    def is_not_cond_challenge(cond):
        return ((cond.operand1Type != OperandTypes.systemVariable or cond.operand1Value != SystemVariable.challengeId) and
                (cond.operand2Type != OperandTypes.systemVariable or cond.operand2Value != SystemVariable.challengeId))
    
    return filter(is_not_cond_challenge,cond_list)

# Takes in a condition which is not an AND, OR, or NOT, and makes it into a handy tuple for easy web display
def leaf_condition_to_tuple(cond):
    if (cond.operation not in leaf_condition_operators):
        return "Error, this is not a leaf condition, it is an AND, OR, or NOT"
    #first operand in a condition should always be a system variable
    #TODO: Make code work even when this is backwards
    op1 =SystemVariable.systemVariables[cond.operand1Value]['name']          
    op = cond.operation
    if (cond.operand2Type == OperandTypes.immediateInteger):
        op2 = str(cond.operand2Value)
        op2ind = 'constant'
    elif (cond.operand2Type == OperandTypes.floatConstant):
        op2 = str(FloatConstants.objects.get(pk=cond.operand2Value))
        op2ind = 'constant'
    elif (cond.operand2Type == OperandTypes.stringConstant):
        op2 = str(StringConstants.objects.get(pk=cond.operand2Value))
        op2ind = 'constant'
    elif (cond.operand2Type == OperandTypes.systemVariable):
        op2 = SystemVariable.systemVariables[cond.operand2Value]['name'] 
        op2ind = 'systemVariable'       
    return (op1, op, op2, op2ind)   # ind is indicating whether it will be displayed as a textfield value or system variables selection

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
            subCondIndexList = string[3:-1].split(",")
            cond = Conditions()
            cond.operation = letter_to_operation[string[0]]
            cond.operand1Type = OperandTypes.conditionSet
            cond.operand1Value = 0
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
            cond = Conditions()
            if string[2] == "*":
                cond.operation = "FOR_ALL"
            elif string[2] == "1":
                cond.operation = "FOR_ANY"
            else:
                return None
            parts = string[3:].split(".")
            if parts[1] == "activity":
                cond.operand1Type == OperandTypes.activitySet
            elif parts[1] == "challenge":
                cond.operand1Type == OperandTypes.challengeSet
            else:
                return None
            if parts[2] == "*":
                cond.operand1Value = 0
            else:
                cond.operand1Value = 1
                subThingieIndexList = parts[2][1:-1].split(",")
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
                else:
                    return None
            subCond = condTable[int(parts[3])]
            if subCond is None:
                return None
            else:
                cond.operand2Type = OperandTypes.condition
                cond.operand2Value = int(stringToCondHelper(subCond).conditionID)
            cond.save()
            return cond;
        
                