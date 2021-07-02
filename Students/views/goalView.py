'''
Created on 2/18/2019

Modeled after announcementCreateView.py

@author: jcherry
'''

import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from Badges.enums import Action, ObjectTypes, OperandTypes
from Badges.models import ActionArguments, Conditions, RuleEvents, Rules, CourseConfigParams
from Badges.periodicVariables import PeriodicVariables
from Badges.systemVariables import SystemVariable
from Badges.tasks import create_goal_expire_event
from Instructors.views.debugSysVars import getSysValues
from Instructors.views.utils import current_localtime
from Students.models import StudentGoalSetting, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def goal_view(request):
    
    context_dict, current_course = studentInitialContextDict(request)
    ccparams=CourseConfigParams.objects.get(courseID=current_course)
    
    #If structure checks course config to see what combination of VC and duels/callouts 
    # are available, if any, to display goals appropriately
    if not ccparams.virtualCurrencyUsed and not ccparams.classmatesChallenges:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True and sysvar['index'] != 978 and sysvar['index'] != 968 and sysvar['index'] != 960 and sysvar['index'] != 957 and sysvar['index'] != 956 and sysvar['index'] != 953]

    elif not ccparams.virtualCurrencyUsed and ccparams.classmatesChallenges:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True and sysvar['index'] != 978 and sysvar['index'] != 968]

    elif ccparams.virtualCurrencyUsed and not ccparams.classmatesChallenges:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True and sysvar['index'] != 960 and sysvar['index'] != 957 and sysvar['index'] != 956 and sysvar['index'] != 953]

    else:        
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True]

    context_dict['goal_variables'] = goal_list
                                    
    if request.method == 'POST':

        if 'goal_target' in request.POST:
            student_duplicate_goal = StudentGoalSetting.objects.filter(targetExact=bool(int(request.POST.get("target_exact"))))
            
            if student_duplicate_goal.exists():
                return redirect('goalslist')

        if 'goal_id' in request.POST:
            goal = StudentGoalSetting.objects.get(pk=int(request.POST['goal_id']))
            delete_goal_rule(goal)
            if 'delete' in request.POST:
                goal.delete()
                return redirect('goalslist')
        else:
            goal = StudentGoalSetting()

        goal_variable_index = int(request.POST['goal_variable'])
        goal_target = float(request.POST['goal_target'])

        goal.courseID = current_course
        goal.studentID = context_dict['student']
        goal.goalVariable = goal_variable_index
        goal.targetedNumber = goal_target
        goal.targetExact = bool(int(request.POST.get("target_exact")))
        goal.timestamp = current_localtime().replace(second=0, microsecond=0) 
        goal.progressToGoal = process_goal(current_course, context_dict['student'], goal_variable_index)
        goal.recurringGoal = "recurring_goal" in request.POST
        goal.completed = False

        if goal.targetExact:
            target = goal_target
        else:
            target = goal.progressToGoal + goal_target

        game_rule = create_goal_rule(current_course, goal_type_to_name(goal.goalVariable), goal_variable_index, target)
        goal.ruleID = game_rule
        goal.save()  

        create_goal_expire_event(request, context_dict['student'].pk, goal.pk, goal.timestamp + timedelta(days=7), request.session['django_timezone'])
                
        return redirect('goalslist')

    elif request.method == 'GET':
        context_dict['target_exact'] = True
        if 'goal_id' in request.GET:
            goal = StudentGoalSetting.objects.get(pk=int(request.GET['goal_id']))

            context_dict['goal_id'] = request.GET['goal_id']
            context_dict['goal_variable'] = goal.goalVariable
            context_dict['goal_target'] = goal.targetedNumber
            context_dict['target_exact'] = goal.targetExact

            context_dict['recurring_goal'] = goal.recurringGoal                      

    return render(request,'Students/GoalsCreationForm.html', context_dict)

def process_goal(course, student, var):
    result = getSysValues(student, var, ObjectTypes.none, course)[0][4]
    return result

def goal_type_to_name(goal_type):
    goal_variables = [sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True]
    
    goal_var = [var['displayName'] for var in goal_variables if var['index'] == goal_type]

    return goal_var[0] if len(goal_var) == 1 else "invalid"

def create_goal_rule(current_course, goal_name, goal_variable_index, goal_target):
    system_var_events = SystemVariable.systemVariables[goal_variable_index]['eventsWhichCanChangeThis'][ObjectTypes.none]

    condition = Conditions()
    condition.courseID = current_course
    condition.operation = '>='
    condition.operand1Type = OperandTypes.systemVariable
    condition.operand1Value = goal_variable_index
    condition.operand2Type = OperandTypes.immediateInteger
    condition.operand2Value = float(goal_target)
    condition.save()
                                    
    # Save game rule to the Rules table
    gameRule = Rules()
    gameRule.conditionID = condition
    gameRule.actionID = Action.completeGoal
    gameRule.courseID = current_course
    gameRule.save()
    
    # Create a goal notification for each event
    for event in system_var_events:
        ruleEvent = RuleEvents()
        ruleEvent.rule = gameRule
        ruleEvent.event = event
        ruleEvent.save()
        
        # First argument is the goal name for the notification
        actionArgs = ActionArguments()
        actionArgs.ruleID = gameRule
        actionArgs.sequenceNumber = 1
        actionArgs.argumentValue = goal_name
        actionArgs.save()

        # # Second argument is the related link for the notification
        # actionArgs = ActionArguments()
        # actionArgs.ruleID = gameRule
        # actionArgs.sequenceNumber = 1
        # actionArgs.argumentValue = '/oneUp/students/goalslist'
        # actionArgs.save()
    return gameRule

def delete_goal_rule(goal):
    if goal.ruleID == None:
        return
    # Delete the conditions and everything else related to the rule
    goal.ruleID.delete_related()
    # Then we delete the rule itself
    goal.ruleID.delete()
    goal.ruleID = None
    goal.save()

def mark_goal_complete(goal):
    delete_goal_rule(goal)
    goal.completed = True
    goal.save()
