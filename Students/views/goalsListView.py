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
from datetime import datetime
from oneUp.decorators import instructorsCheck   
from Students.models import StudentGoalSetting

# Added boolean to check if viewing from announcements page or course home page
def goalsList(currentCourse, context_dict, courseHome):

    studentGoal_ID = []      
    student_ID = []
    start_date = []
    end_date = []
    goal_Type = []
    targeted_Number = []
        
    goals = StudentGoalSetting.objects.filter(courseID=currentCourse).order_by('-startTimestamp')
    index = 0
    if not courseHome: # Shows all the announcements
        for goal in goals:
            studentGoal_ID.append(goal.studentGoalID) #pk
            student_ID.append(goal.studentID)
            start_date.append(goal.timestamp)
            # if default end date (= unlimited) is stored, we don't want to display it on the webpage                   
            end_date = goal.timestamp
            end_date.append(goal.timestamp)
            
            #end_date calculation function here
            
            goal_Type.append(goal.goalType)
            targeted_Number.append(goal.targetedNumber)
    else: # Only shows the first three
        for goal in goals:
            if index < 1:
                studentGoal_ID.append(goal.studentGoalID) #pk
                student_ID.append(goal.studentID)
                start_date.append(goal.timestamp)
                end_date.append(goal.timestamp)
                goal_Type.append(goal.goalType)
                targeted_Number.append(goal.targetedNumber)
                index += 1
    
      
    # The range part is the index numbers.
    context_dict['goal_range'] = zip(range(1,goals.count()+1),studentGoal_ID,student_ID,start_date,end_date,goal_Type,targeted_Number)
    return context_dict

    
@login_required
def announcementList(request):

    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForGoalList(currentCourse, context_dict, False)
    
    return render(request,'Instructors/GoalsList.html', context_dict)



            
    
    
