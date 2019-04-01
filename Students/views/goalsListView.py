'''
Created on February 2, 2019

Based on announcementsListView.html as a template

@author: James Cherry
'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Announcements, Instructors, Courses, Goals
from Instructors.views.utils import utcDate, initialContextDict
from Instructors.constants import default_time_str
from datetime import datetime, date, time, timedelta
from oneUp.decorators import instructorsCheck   
from Students.models import StudentGoalSetting
from Students.views.utils import studentInitialContextDict
from Students.views.allAnnouncementsView import createContextForAnnouncementList

from Students.models import StudentGoalSetting
from Badges.enums import Goal
from Badges import systemVariables
from Students.views import goalCreateView


# Added boolean to check if viewing from announcements page or course home page
def createContextForGoalsList(currentCourse, context_dict, courseHome):

    studentGoal_ID = []      
    student_ID = []
    course_ID = []
    start_date = []
    edit_allowed = []
    end_date = []
    goal_Type = []
    targeted_Number = []
    goal_progress = []
    goal_status = []
        
    goals = StudentGoalSetting.objects.filter(studentID=context_dict['student'],courseID=currentCourse).order_by('-timestamp')
    index = 0
    if not courseHome: # Shows all the announcements
        for goal in goals:
            studentGoal_ID.append(goal.studentGoalID) #pk
            student_ID.append(goal.studentID)
            start_date.append(goal.timestamp.strftime('%m/%d/%y'))
            course_ID.append(goal.courseID)
            # if default end date (= unlimited) is stored, we don't want to display it on the webpage  
            
            edit_allowed.append(editGoal(goal.timestamp))
                             
            endDate = goal.timestamp + timedelta(days=7)
            end_date.append(endDate.strftime('%m/%d/%y'))           
            #end_date calculation function here            
            goal_Type.append(goalTypeToString(goal.goalType))
            targeted_Number.append(goal.targetedNumber)            
                                  
            progressPercent = calculateProgress(goal.progressToGoal, goal.goalType, goal.courseID, goal.studentID, goal.targetedNumber)
            goal_progress.append(progressPercent)
            goal_status.append(goalStatus(progressPercent, endDate))
            
    else: # Only shows the first three
        for goal in goals:
            if index < 1:
                studentGoal_ID.append(goal.studentGoalID) #pk
                student_ID.append(goal.studentID)
                course_ID.append(goal.courseID)
                
                edit_allowed.append(editGoal(goal.timestamp))
                
                start_date.append(goal.timestamp.strftime('%m/%d/%y'))
                endDate = goal.timestamp + timedelta(days=7)
                end_date.append(endDate.strftime('%m/%d/%y')) 
                goal_Type.append(goalTypeToString(goal.goalType))
                targeted_Number.append(goal.targetedNumber)
                
                progressPercent = calculateProgress(goal.progressToGoal, goal.goalType, goal.courseID, goal.studentID, goal.targetedNumber)
                goal_progress.append(progressPercent)
                goal_status.append(goalStatus(progressPercent, endDate))
                index += 1
    
      
    # The range part is the index numbers.
    context_dict['goal_range'] = zip(range(1,goals.count()+1),studentGoal_ID,student_ID,course_ID,start_date,end_date,goal_Type,targeted_Number,goal_progress,goal_status,edit_allowed)
    return context_dict

    
@login_required
def goalsList(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    context_dict = createContextForGoalsList(currentCourse, context_dict, False)
    
    return render(request,'Students/GoalsList.html', context_dict)

def goalTypeToString(gt):
    genums = Goal.goals
    #gname = 'Blank'    
    
    return genums[gt].get('displayName')

def calculateProgress(initialGoalTarget, goalType, course, student, target):
    goalType = str(goalType)
    
    newProgress = goalCreateView.goalProgressFxn(goalType, course, student)
    
    progressPercent = ((newProgress - initialGoalTarget) / target) * 100
    
    return round(progressPercent, 0)

def goalStatus(progressPercent, endDate):
    if (progressPercent >= 100):
        return "Completed"
    elif (utcDate() >= endDate):
        return "Failed"
    else:
        return "In Progress"
    
def editGoal(startDate):
    editDeadline = startDate + timedelta(hours=24)
    
    if (utcDate() < editDeadline):
        return True
    else:
        return False  
    
    