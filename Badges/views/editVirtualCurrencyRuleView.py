'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments
from Instructors.models import Challenges,Courses, Activities
from Badges.enums import SystemVariable, dict_dict_to_zipped_list, displayCircumstance

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import get_mandatory_conditions_without_or_and_not, filter_out_associated_challenges, leaf_condition_to_tuple,\
    get_associated_challenge_if_exists, get_associated_activity_if_exists
from setuptools.command.build_ext import if_dl

    
def EditVirtualCurrencyRule(request):
 
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
        
    if request.GET:

        # Getting the Rule information which has been selected
        if request.GET['vcRuleID']:
            vcRuleID = request.GET['vcRuleID']
            rule = VirtualCurrencyRuleInfo.objects.get(vcRuleID=vcRuleID, courseID=currentCourse)
            
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                context_dict["vcAmount"] = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
            else:
                context_dict["vcAmount"] = 0
                
            condition = rule.ruleID.conditionID
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
                
            sysIndex = []
            sysDisplayName = []
            sysEnabled = []
            condOperation = []
            condValues = []
            systemVariableObjects= dict_dict_to_zipped_list(SystemVariable.systemVariables,['index','name', 'displayName', 'displayCircumstances'])  
            # Loop through the system variables for virtual currency
            for i, name, sysVars, display in systemVariableObjects:
                for key, v in display.items():
                    if key == displayCircumstance.virtualCurrency:
                        sysIndex.append(i)
                        sysDisplayName.append(sysVars)
                        # Set system variable enabled flag to true if condition name is the same
                        found = False
                        for c in conditions:
                            if c[0] == name:
                                sysEnabled.append(True)
                                condOperation.append(c[1])
                                condValues.append(c[2])
                                found = True
                        if found == False:
                            sysEnabled.append(False)
                            condOperation.append('==')
                            condValues.append(0)
                            
            (has_challenge,associated_challenge) = get_associated_challenge_if_exists(condition)
            (has_activity,associated_activity) = get_associated_activity_if_exists(condition)
            
            # Set up a list of challenge objects for the dropbox, excluding the special "Unassigned Problems" challenge
            challengeObjects=[]  
            activityObjects=[]              
            chall=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse) # Unassigned problems to be excluded
            for challID in chall:
                unassignID = challID.challengeID

            challenges = Challenges.objects.filter(courseID=currentCourse)       
            for challenge in challenges:
                if challenge.challengeID != unassignID:    
                    challengeObjects.append(challenge)
                    print("*challenge: "+str(challenge.challengeID))
            activities = Activities.objects.filter(courseID=currentCourse)
            for activity in activities:
                activityObjects.append(activity)  
                print("activity: "+str(activity))       

    # The range part is the index numbers.
    context_dict['systemVariables'] = zip(range(1, len(sysIndex)+1), sysIndex, sysDisplayName, sysEnabled, condOperation, condValues)
    context_dict['challenges'] = zip(range(1,challenges.count()+1),challengeObjects)
    context_dict['activities'] = zip(range(1,activities.count()+1),activityObjects)    
    context_dict['vcRule'] = rule
    context_dict['conditions'] = zip(range(1,len(conditions)+1),conditions)
#    context_dict['assignChallenges'] = zip(range(1,len(assignChallObjects)+1),assignChallObjects)
    context_dict['has_challenge'] = has_challenge
    context_dict['associated_challenge'] = associated_challenge
    context_dict['has_activity'] = has_activity
    context_dict['associated_activity'] = associated_activity
    
    return render(request,'Badges/EditVirtualCurrencyRule.html', context_dict)