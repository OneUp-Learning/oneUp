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
    if (cond.operation in leaf_condition_operators):
        events = []
        if (cond.operand1Type == OperandTypes.systemVariable):
            events.extend(get_events_for_system_variable(cond.operand1Value))
        if (cond.operand2Type == OperandTypes.systemVariable):
            events.extend(get_events_for_system_variable(cond.operand2Value))
        return events
    elif (cond.operation in binary_condition_operators):
        cond1events = get_events_for_condition(Conditions.objects.get(pk=cond.operand1Value))
        cond2events = get_events_for_condition(Conditions.objects.get(pk=cond.operand2Value))
        return cond1events + cond2events
    elif (cond.operation in unary_condition_operators):
        return get_events_for_condition(Conditions.objects.get(pk=cond.operand1Value))
    else:
        return "ERROR: Invalid operator in condition.  Should be one of '==','<','>','<=','>=','!='."
    

def 