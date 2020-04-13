'''
Created on 2/1/2019

Based on announcementsListView.html as a template

@author: James Cherry
'''
import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Badges.periodicVariables import PeriodicVariables
from Badges.systemVariables import SystemVariable
from Instructors.views.utils import utcDate
from Students.models import StudentGoalSetting
from Students.views.goalView import process_goal
from Students.views.utils import studentInitialContextDict

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def goals_list(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    context_dict = createContextForGoalsList(currentCourse, context_dict, False)
    
    return render(request,'Students/GoalsList.html', context_dict)

def createContextForGoalsList(currentCourse, context_dict, courseHome):
    if not 'student' in context_dict:
        logger.error("You must pass student object through context_dict")
        return context_dict

    goal_ID = []      
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

    goal_variables = [sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True] \
                    + [PeriodicVariables.periodicVariables[PeriodicVariables.xp_ranking]]

    limit = None
    if courseHome:
        limit = 3
    
    current_time = utcDate()
    for goal in goals:

        if limit and limit == 0:
            break

        goal_ID.append(goal.studentGoalID) #pk
        student_ID.append(goal.studentID)
        # start_date.append(goal.timestamp.strftime('%m/%d/%y'))
        start_date.append(goal.timestamp)
        course_ID.append(goal.courseID) 
                                                    
        endDate = goal.timestamp + timedelta(days=7)
        # end_date.append(endDate.strftime('%m/%d/%y'))
        end_date.append(endDate)               
        goal_var = [var['displayName'] for var in goal_variables if var['index'] == goal.goalType]
        goal_name.append(goal_var[0])
        goal_target.append(goal.targetedNumber) 
                        
        progress_percentage = calculate_progress(goal.progressToGoal, goal.goalType, goal.courseID, goal.studentID, goal.targetedNumber)  
        goal_progress.append(min(progress_percentage, 100))
        
        status = goal_status_str(progress_percentage, endDate, current_time)
        goal_status.append(status)
        can_edit.append(status == 'In Progress')
        
        recurring_goal.append("Yes" if goal.recurringGoal else "No")    
        
        if current_time >= endDate:
            if limit:
                limit -= 1
            if goal.recurringGoal:
                new_recurring_goal(goal, endDate)
                goal.recurringGoal = False
                goal.save() 
      
    status_order = ['In Progress',  'Not Achieved', 'Completed']
    context_dict['goal_range'] = sorted(list(zip(range(1,goals.count()+1),goal_ID,student_ID,course_ID,start_date,end_date,goal_name,goal_target,goal_progress,goal_status,recurring_goal, can_edit)), key=lambda x: (status_order.index(x[9]), x[5]))
    return context_dict

def calculate_progress(starting_progress, goal_var, course, student, goal_target):
    
    new_progression = process_goal(course, student, goal_var)
    
    percentage = ((new_progression - starting_progress) / goal_target) * 100
    
    return round(percentage, 0)

def goal_status_str(progress_percentage, end_date, current_time):
    if (progress_percentage >= 100):
        return "Completed"
    elif (current_time >= end_date):
        return "Not Achieved"
    else:
        return "In Progress"
    
def new_recurring_goal(goal, end_date):

    duplicate_goal = StudentGoalSetting()        
    duplicate_goal.courseID = goal.courseID
    duplicate_goal.studentID = goal.studentID
    duplicate_goal.goalType = goal.goalType
    duplicate_goal.targetedNumber = goal.targetedNumber
    duplicate_goal.timestamp = end_date  
    duplicate_goal.progressToGoal = goal.progressToGoal
    duplicate_goal.recurringGoal = True       
    duplicate_goal.save()
