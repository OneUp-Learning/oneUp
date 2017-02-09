'''
Created on Jan 27, 2017

@author: kirwin
'''

from Badges.enums import SystemVariable, Event, OperandTypes
from Badges.models import Conditions

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
def get_mandatory_conditions_without_or_and_not():
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
    cond_count = len(cond_list)
    if cond_count == 0:
        return "Error.  At least one condition must be present."
    elif cond_count == 1:
        return cond_list[1]
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
def get_associated_challenge(cond):
    mand_conds = get_mandatory_conditions(cond)
    for mc in mand_conds:
        if (    mc.operand1Type == OperandTypes.systemVariable
                and mc.operand1Value == SystemVariable.challengeId
                and mc.operand2Type == OperandTypes.immediateInteger
        ):
            return mc.operand2Value
        if (    mc.operand2Type == OperandTypes.systemVariable
                and mc.operand2Value == SystemVariable.challengeId
                and mc.operand2Type == OperandTypes.immediateInteger
        ):
            return mc.operand1Value

    # We have finished the whole loop and found nothing/
    return "No associated challenge found"