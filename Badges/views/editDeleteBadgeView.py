'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render

from Badges.models import Badges, Conditions, FloatConstants, StringConstants
from Instructors.models import Challenges,Courses
from Badges.enums import SystemVariable, dict_dict_to_zipped_list, OperandTypes
from Badges.views import createBadgeView

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import get_mandatory_conditions_without_or_and_not, filter_out_associated_challenges, leaf_condition_to_tuple,\
    get_associated_challenge_if_exists
from setuptools.command.build_ext import if_dl

# conditions is a matrix of triples: firstOperand, operation, secondOperand
def ConditionTree(currCondition):
    
    print ("0:  " + str(currCondition))
    operation = currCondition.operation
    op2type = currCondition.operand2Type
    op2value = currCondition.operand2Value       
    if (not operation == 'AND'):
        # a proper condition, must add components to lists
        #first operand in a condition is always a system variable
        op1 =SystemVariable.systemVariables[currCondition.operand1Value]['name']          
        op = operation
        if (op2type == OperandTypes.immediateInteger):
            op2 = str(op2value)
            op2ind = 'constant'
        elif (op2type == OperandTypes.floatConstant):
            op2 = str(FloatConstants.objects.get(pk=op2value))
            op2ind = 'constant'
        elif (op2type == OperandTypes.stringConstant):
            op2 = str(StringConstants.objects.get(pk=op2value))
            op2ind = 'constant'
        elif (op2type == OperandTypes.systemVariable):
            op2 = SystemVariable.systemVariables[op2value]['name'] 
            op2ind = 'systemVariable'       
        return [(op1, op, op2, op2ind)]   # ind is indicating whether it will be displayed as a textfield value or system variables selection
    
    # operation AND
    l1 = ConditionTree(Conditions.objects.get(pk=currCondition.operand1Value))
    l2 = ConditionTree(Conditions.objects.get(pk=currCondition.operand2Value))

    return l1 + l2
    
def EditDeleteBadge(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
    
    conditions = []
    
    createBadgeView.extractPaths(context_dict)
    
    if request.GET:

        # Getting the Badge information which has been selected
        if request.GET['badgeID']:
            badgeId = request.GET['badgeID']
            badge = Badges.objects.get(badgeID=badgeId)
            condition = badge.ruleID.conditionID
            print("Condition: "+str(condition))
                 
            ##Fill in the condition matrix
            #conditions = ConditionTree(condition)
            conditions_list = get_mandatory_conditions_without_or_and_not(condition)
            conditions_list = filter_out_associated_challenges(conditions_list)
            conditions = list(map(leaf_condition_to_tuple,conditions_list))
            # Test print
            print('conditions:')
            for c in conditions:
                print(c)
                
            systemVariableObjects= dict_dict_to_zipped_list(SystemVariable.systemVariables,['index','name', 'displayName'])  
            
            #assignedChallenges = BadgeChallenges.objects.filter(badgeID=badgeId)
            #print("assign chall obj: "+str(assignedChallenges))
            #for assignChallenge in assignedChallenges:
            #    assignChallObjects.append(assignChallenge.challengeID.challengeID)
            #    print("asschall.cid.cid:"+str(assignChallenge.challengeID))
            (has_challenge,associated_challenge) = get_associated_challenge_if_exists(condition)

            # Set up a list of challenge objects for the dropbox, excluding the special "Unassigned Problems" challenge
            challengeObjects=[]            
            chall=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse) # Unassigned problems to be excluded
            for challID in chall:
                unassignID = challID.challengeID

            challenges = Challenges.objects.filter(courseID=currentCourse)       
            for challenge in challenges:
                if challenge.challengeID != unassignID:    
                    challengeObjects.append(challenge)
                    print("*challenge: "+str(challenge.challengeID))
                
    # The range part is the index numbers.
    context_dict['systemVariables'] = systemVariableObjects
    context_dict['challenges'] = zip(range(1,challenges.count()+1),challengeObjects)    
    context_dict['badge'] = badge
    context_dict['conditions'] = zip(range(1,len(conditions)+1),conditions)
#    context_dict['assignChallenges'] = zip(range(1,len(assignChallObjects)+1),assignChallObjects)
    context_dict['has_challenge'] = has_challenge
    context_dict['associated_challenge'] = associated_challenge
    #context_dict['num_Conditions'] = "1"
    context_dict['num_Conditions'] = len(conditions)
    
    return render(request,'Badges/EditDeleteBadge.html', context_dict)