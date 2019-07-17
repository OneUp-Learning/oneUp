'''
Created on 2/1/2019

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
from Students.models import StudentGoalSetting, Student
from Students.views.utils import studentInitialContextDict
from Students.views.allAnnouncementsView import createContextForAnnouncementList

from Students.models import StudentGoalSetting
from Badges.enums import Goal
from Badges import systemVariables
from Students.views import goalCreateView
from Students.views.goalCreateView import goalCreate


# Added boolean to check if viewing from announcements page or course home page
def createContextForGoalsList(currentCourse, context_dict, courseHome, user):

    if (not instructorsCheck(user)):
        student = Student.objects.get(user=user)
    else:
        student = context_dict["student"]

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
    recurring_goal = []
        
    goals = StudentGoalSetting.objects.filter(studentID=student,courseID=currentCourse).order_by('-timestamp')
    
    
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
            
            if (progressPercent <= 100): 
                goal_progress.append(progressPercent)
            else:
                goal_progress.append(100)
            
            status = goalStatus(progressPercent, endDate)
            goal_status.append(status)
            
            recurring_goal.append(goal.recurringGoal)    
            
            if (utcDate() >= endDate):
                goalRecurrence(goal.recurringGoal, goal.courseID, goal.studentID, goal.goalType, goal.targetedNumber, goal.progressToGoal, endDate)
                sgi = goal.studentGoalID
                goal = StudentGoalSetting.objects.get(pk=int(sgi))
                goal.recurringGoal = False
                goal.save()
            
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
                
                status = goalStatus(progressPercent, endDate)
                goal_status.append(status)
                
                recurring_goal.append(goal.recurringGoal)
                
                if (utcDate() >= endDate):
                    index += 1    
      
    # The range part is the index numbers.
    print (student_ID)
    context_dict['goal_range'] = zip(range(1,goals.count()+1),studentGoal_ID,student_ID,course_ID,start_date,end_date,goal_Type,targeted_Number,goal_progress,goal_status,edit_allowed,recurring_goal)
    return context_dict

    
@login_required
def goalsList(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    context_dict = createContextForGoalsList(currentCourse, context_dict, False, request.user)
    
    return render(request,'Students/GoalsList.html', context_dict)

def goalTypeToString(gt):
    genums = Goal.goals
    #gname = 'Blank'    
    return genums[gt].get('displayName')

def calculateProgress(initialGoalTarget, goalType, course, student, target):
    gcv = goalCreateView
    
    newProgress = gcv.goalProgressFxn(goalType, course, student)
    
    progressPercent = ((newProgress - initialGoalTarget) / target) * 100
    
    return round(progressPercent, 0)

def goalStatus(progressPercent, endDate):
    if (progressPercent >= 100):
        return "Completed"
    elif (utcDate() >= endDate):
        return "Not Achieved"
    else:
        return "In Progress"
    
def editGoal(startDate):
    editDeadline = startDate + timedelta(hours=24)
    
    if (utcDate() < editDeadline):
        return True
    else:
        return False  
    
def goalRecurrence(recur, course, student, goalType, target, progress, endDate):
    if (recur):
        goal = StudentGoalSetting()        
        goal.courseID = course
        goal.studentID = student
        goal.goalType = goalType
        goal.targetedNumber = target
        goal.timestamp = endDate  
        print("Goal endDate is: ", endDate) 
        print("New goal start date is: ", goal.timestamp)      
        goal.progressToGoal = progress
        goal.recurringGoal = recur       
        goal.save();  #Writes to database.
    
    