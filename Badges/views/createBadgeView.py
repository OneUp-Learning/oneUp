'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render
import glob, os
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Courses
from Badges.enums import SystemVariable, dict_dict_to_zipped_list, OperandTypes
from Instructors.views.utils import initialContextDict
from Badges.conditions_util import setUpContextDictForConditions,\
    databaseConditionToJSONString
from Badges.models import Conditions


# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def CreateBadge(request):
    
    context_dict,current_course = initialContextDict(request);
    
    extractPaths(context_dict)

    context_dict = setUpContextDictForConditions(context_dict,current_course)

    context_dict['initialCond'] = databaseConditionToJSONString(makeTestCondtition(current_course))

    return render(request,'Badges/CreateBadge.html', context_dict)

def extractPaths(context_dict): #function used to get the names from the file location
    imagePath = []
    
    for name in glob.glob('static/images/badges/*'):
        name = name.replace("\\","/")
        imagePath.append(name)
        print(name)
    
    context_dict["imagePaths"] = zip(range(1,len(imagePath)+1), imagePath)

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