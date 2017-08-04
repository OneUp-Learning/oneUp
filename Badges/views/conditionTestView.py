from django.shortcuts import render
from Badges.enums import system_variable_type_to_HTML_type, ObjectTypes,\
    OperandTypes
from Badges.systemVariables import SystemVariable
from Badges.conditions_util import setUpContextDictForConditions, databaseConditionToJSONString,\
    stringAndPostDictToCondition
from Badges.models import Conditions
from Instructors.models import Activities, Challenges, Courses
from Instructors.views.utils import initialContextDict


def makeTestCondtition(course):
    testCond = Conditions()
    testCond.courseID = course
    testCond.operation = ">"
    testCond.operand1Type = OperandTypes.systemVariable
    testCond.operand1Value = SystemVariable.consecutiveClassesAttended
    testCond.operand2Type = OperandTypes.immediateInteger
    testCond.operand2Value = 5
    testCond.save()
    return testCond

testCondition = None

def conditionTestView(request):
    global testCondition
    
    context_dict,current_course = initialContextDict(request);
    
    context_dict = setUpContextDictForConditions(context_dict,current_course)
    
    if testCondition is None:
        testCondition = makeTestCondtition(current_course)
    
    if request.POST:
        print ("POST RECEIVED")
        print("cond-cond-string="+request.POST['cond-cond-string'])
        print("test Condtion PK: "+str(testCondition.conditionID))
        try:
            testCondition.delete()
        except:
            testCondition = None
        testCondition = stringAndPostDictToCondition(request.POST['cond-cond-string'],request.POST,current_course)
    
    context_dict['initialCond'] = databaseConditionToJSONString(testCondition)
    
    return render(request,'Badges/conditionInterface.html', context_dict)
