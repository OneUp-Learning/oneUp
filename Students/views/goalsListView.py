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


# Added boolean to check if viewing from announcements page or course home page
def createContextForGoalsList(currentCourse, context_dict, courseHome):

    studentGoal_ID = []      
    student_ID = []
    course_ID = []
    start_date = []
    end_date = []
    goal_Type = []
    targeted_Number = []
    goal_progress = []
        
    goals = StudentGoalSetting.objects.filter(studentID=context_dict['student'],courseID=currentCourse).order_by('-timestamp')
    index = 0
    if not courseHome: # Shows all the announcements
        for goal in goals:
            studentGoal_ID.append(goal.studentGoalID) #pk
            student_ID.append(goal.studentID)
            start_date.append(goal.timestamp.strftime('%m/%d/%y'))
            course_ID.append(goal.courseID)
            # if default end date (= unlimited) is stored, we don't want to display it on the webpage                   
            endDate = goal.timestamp + timedelta(days=7)
            end_date.append(endDate.strftime('%m/%d/%y'))            
            #end_date calculation function here            
            goal_Type.append(goalTypeToString(goal.goalType))
            targeted_Number.append(goal.targetedNumber)
            goal_progress.append(goal.progressToGoal)
            
    else: # Only shows the first three
        for goal in goals:
            if index < 1:
                studentGoal_ID.append(goal.studentGoalID) #pk
                student_ID.append(goal.studentID)
                course_ID.append(goal.courseID)
                start_date.append(goal.timestamp.strftime('%m/%d/%y'))
                endDate = goal.timestamp + timedelta(days=7)
                end_date.append(endDate.strftime('%m/%d/%y'))
                goal_Type.append(goalTypeToString(goal.goalType))
                targeted_Number.append(goal.targetedNumber)
                goal_progress.append(goal.progressToGoal)
                index += 1
    
      
    # The range part is the index numbers.
    context_dict['goal_range'] = zip(range(1,goals.count()+1),studentGoal_ID,student_ID,course_ID,start_date,end_date,goal_Type,targeted_Number, goal_progress)
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
    
    
