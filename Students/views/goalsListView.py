'''
Created on 2/1/2019

Based on announcementsListView.html as a template

@author: James Cherry
'''
import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from Badges.periodicVariables import PeriodicVariables
from Badges.systemVariables import SystemVariable
from Badges.tasks import create_goal_expire_event
from Instructors.views.utils import current_localtime, datetime_to_local
from Students.models import StudentGoalSetting
from Students.views.goalView import (create_goal_rule, goal_type_to_name,
                                     mark_goal_complete, process_goal)
from Students.views.utils import studentInitialContextDict

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def goals_list(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    context_dict = createContextForGoalsList(request, currentCourse, context_dict, False)
    
    return render(request,'Students/GoalsList.html', context_dict)

def createContextForGoalsList(request, currentCourse, context_dict, courseHome):
    if not 'student' in context_dict:
        logger.error("You must pass student object through context_dict")
        return context_dict

    goal_ID = []  
    targetExact = []    
    student_ID = []
    course_ID = []
    start_date = []
    end_date = []
    goal_name = []
    goal_target = []
    goal_progress = []
    goal_status = []
    recurring_goal = []
    can_edit = []

    student = context_dict['student']
    goals = StudentGoalSetting.objects.filter(studentID=student,courseID=currentCourse).order_by('-timestamp')

    current_time = current_localtime()
    for goal in goals:

        goal_ID.append(goal.studentGoalID) #pk
        student_ID.append(goal.studentID)
        start_date.append(goal.timestamp)
        course_ID.append(goal.courseID) 
        targetExact.append(goal.targetExact)
                                                    
        endDate = datetime_to_local(goal.timestamp) + timedelta(days=7)
        end_date.append(endDate)               
        goal_name.append(goal_type_to_name(goal.goalVariable))
        goal_target.append(goal.targetedNumber) 
        if goal.targetExact:
            target = goal.targetedNumber
        else:
            target = goal.progressToGoal + goal.targetedNumber

        progress_percentage = calculate_progress(goal)  
        goal_progress.append(min(progress_percentage, 100))
        
        status = goal_status_str(progress_percentage, endDate, goal.completed, current_time)
        goal_status.append(status)
        can_edit.append(status == 'In Progress')
        
        recurring_goal.append("Yes" if goal.recurringGoal else "No")    

        if current_time >= endDate:
            if goal.recurringGoal:
                # Create new recurring goal
                duplicate_goal = StudentGoalSetting()        
                duplicate_goal.courseID = goal.courseID
                duplicate_goal.studentID = goal.studentID
                duplicate_goal.goalVariable = goal.goalVariable
                duplicate_goal.targetedNumber = goal.targetedNumber
                duplicate_goal.timestamp = endDate
                duplicate_goal.targetExact = goal.targetExact  
                duplicate_goal.progressToGoal = process_goal(goal.courseID, goal.studentID, goal.goalVariable)
                duplicate_goal.recurringGoal = True      
                if goal.targetExact:
                    target = goal.targetedNumber
                else:
                    target = duplicate_goal.progressToGoal + goal.targetedNumber
                game_rule = create_goal_rule(goal.courseID, goal_type_to_name(int(goal.goalVariable)), int(goal.goalVariable), target)
                duplicate_goal.ruleID = game_rule
                duplicate_goal.save()

                create_goal_expire_event(request, context_dict['student'].pk, duplicate_goal.pk, duplicate_goal.timestamp + timedelta(days=7), request.session['django_timezone'])

                goal.recurringGoal = False
                mark_goal_complete(goal)
                goal.save() 
      
    status_order = ['In Progress', 'Completed', 'Not Achieved']
    context_dict['goal_range'] = sorted(list(zip(range(1,goals.count()+1),goal_ID,student_ID,course_ID,start_date,end_date,goal_name,goal_target,goal_progress,goal_status,recurring_goal, can_edit,targetExact)), key=lambda x: (status_order.index(x[9]), 0 if x[10] == 'Yes' else 1, x[5] ))
    
    if courseHome:
        limit = 3
        context_dict['goal_range'] = context_dict['goal_range'][:limit]

    return context_dict

def calculate_progress(goal):
    
    new_progression = process_goal(goal.courseID, goal.studentID, goal.goalVariable)
    
    if goal.targetExact:
        percentage = ((new_progression) / max(goal.targetedNumber, 1)) * 100
    else:
        percentage = ((new_progression - goal.progressToGoal) / (goal.targetedNumber)) * 100

    return round(percentage, 1)

def goal_status_str(progress_percentage, end_date, completed, current_time):
    if (progress_percentage >= 100):
        return "Completed"
    elif (current_time >= end_date):
        return "Not Achieved"
    else:
        return "In Progress"
