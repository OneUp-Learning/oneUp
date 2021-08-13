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

## Goal Flags
    ## Attribute
    # * studentGoal - If the goal will be shown to students as a student goal
    
    ## Course Config
    # * badgesUsed - If the goal relies on badges being enabled for availability
    # * teamsEnabled - Teams
    # * adaptationUsed - Adaptation
    # * warmupsUsed - Warm Ups
    # * flashcardsUsed - Flash cards
    # * activitiesUsed - Activities
    # * skillsUsed - Skills
    # * levelingUsed - Leveling Enabled
    
def is_student_goal(sysvar):
    return 'goal_flags' in sysvar and 'studentGoal' in sysvar['goal_flags'] 
    
def fetch_goal_list(ccparams):
    #If structure checks course config to see what combination of VC and duels/callouts 
    # are available, if any, to display goals appropriately
    
    if not ccparams.virtualCurrencyUsed and not ccparams.classmatesChallenges:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if is_student_goal(sysvar) and sysvar['index'] != 978 and sysvar['index'] != 968 and sysvar['index'] != 960 and sysvar['index'] != 957 and sysvar['index'] != 956 and sysvar['index'] != 953]

    elif not ccparams.virtualCurrencyUsed and ccparams.classmatesChallenges:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if is_student_goal(sysvar) and sysvar['index'] != 978 and sysvar['index'] != 968]

    elif ccparams.virtualCurrencyUsed and not ccparams.classmatesChallenges:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if is_student_goal(sysvar) and sysvar['index'] != 960 and sysvar['index'] != 957 and sysvar['index'] != 956 and sysvar['index'] != 953]
    else:
        goal_list=[sysvar for i, sysvar in SystemVariable.systemVariables.items() if is_student_goal(sysvar)]
        
    ccparam_filters = {
        'badgesUsed':ccparams.badgesUsed,
        'teamsEnabled':ccparams.teamsEnabled,
        'adaptationUsed':ccparams.adaptationUsed,
        'warmupsUsed':ccparams.warmupsUsed,
        'flashcardsUsed':ccparams.flashcardsUsed,
        'activitiesUsed':ccparams.activitiesUsed,
        'skillsUsed':ccparams.skillsUsed,
        'levelingUsed':ccparams.levelingUsed,
        'studentGoal':True
        }
    
    filtered_list = []
    
    for current_goal in goal_list:
        goal_can_be_used = True # debounce to flag bad matches
        
        print('current goal' + current_goal['name'])
        for flag in current_goal['goal_flags']: # all student goals have flags
            print('determining flag ' + flag)
            if flag in ccparam_filters and ccparam_filters[flag] == False:
                print('failed check for ' + flag)
                goal_can_be_used = False
            else:
                print('flag '+flag+' passed check as '+str(ccparam_filters[flag]))
                
        if goal_can_be_used == True:
            filtered_list.append(current_goal)
                
    print(filtered_list)
    
    return filtered_list

@login_required
def goal_view(request):
    
    context_dict, current_course = studentInitialContextDict(request)
    ccparams=CourseConfigParams.objects.get(courseID=current_course)
    
    context_dict['goal_variables'] = fetch_goal_list(ccparams)
                                    
    if request.method == 'POST':

        if 'goal_id' in request.POST: # Edit a goal
            goal = StudentGoalSetting.objects.get(pk=int(request.POST['goal_id'])) # Find goal in models
            delete_goal_rule(goal) # Delete associated rules
            if 'delete' in request.POST:
                goal.delete()
                return redirect('goalslist')
        else: # Create new goal
            if 'goal_target' in request.POST:
                student_duplicate_goal = StudentGoalSetting.objects.filter(completed=False, courseID=current_course, studentID=context_dict['student'], goalVariable=int(request.POST['goal_variable']))
                
                print('duplicated goal')
                
                if student_duplicate_goal.exists():
                    return redirect('goalslist')
            
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
    goal_variables = [sysvar for i, sysvar in SystemVariable.systemVariables.items()]
        
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
