'''
Created on 2/18/2019

Modeled after announcementCreateView.py

@author: jcherry
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.utils import utcDate, initialContextDict

#4.2.2019 JC
from Students.models import StudentGoalSetting, StudentRegisteredCourses
from Badges.enums import Goal
from Badges import systemVariables
from Students.views.utils import studentInitialContextDict
from django.template.context_processors import request
from Badges.periodicVariables import studentScore, TimePeriods

@login_required
 
def goalCreate(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = studentInitialContextDict(request)
    genums = Goal.goals
    
    goal_type = []
    goal_display = []
    
    for g in genums:
        goal_type.append(genums[g].get('index'))
        goal_display.append(genums[g].get('displayName'))  
    
    if request.POST:

        # Get the activity from the DB for editing or create a new announcement  
        if 'studentGoalID' in request.POST:
            sgi = request.POST['studentGoalID']
            goal = StudentGoalSetting.objects.get(pk=int(sgi))
        else:
            goal = StudentGoalSetting()
        
        goal.courseID = currentCourse
        goal.studentID = context_dict['student'] #get student ID
        goal.goalType = request.POST['goalType']
        goal.targetedNumber = request.POST['targetedNumber']
        goal.timestamp = utcDate()
        
          
        goal.progressToGoal = goalProgressFxn(goal.goalType, goal.courseID, goal.studentID)  

        goal.recurringGoal = "recurringGoal" in request.POST
        
        goal.save();  #Writes to database.    
                
        return redirect('GoalsList')

    ######################################
    # request.GET 
    elif request.GET:
            
                            
            # If studentGoalId is specified then we load for editing.
            if 'studentGoalID' in request.GET:
                goal = StudentGoalSetting.objects.get(pk=int(request.GET['studentGoalID']))
                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['studentGoalID'] = request.GET['studentGoalID']
                context_dict['goalType'] = genums[goal.goalType].get('index')
                context_dict['goalName'] = genums[goal.goalType].get('displayName')
                context_dict['targetedNumber'] = goal.targetedNumber
                context_dict['recurringGoal'] = goal.recurringGoal
                print(goal.recurringGoal)
                print(context_dict['recurringGoal'])        
    
    else:
        goal_type = []
        goal_display = []
    
        for g in genums:
            goal_type.append(genums[g].get('index'))
            goal_display.append(genums[g].get('displayName'))
            
        context_dict['goaltype_range'] = zip(range(1,len(genums)+1),goal_type,goal_display)
                                    

    return render(request,'Students/GoalsCreationForm.html', context_dict)

def goalProgressFxn(goalType, course, student):
    goalType = str(goalType)
    print (goalType)
    if goalType == str(Goal.warmup10):
        return systemVariables.getNumberOfUniqueWarmupChallengesAttempted(course, student)
    if goalType == str(Goal.warmup70):
        return systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan70Percent(course, student)
    if goalType == str(Goal.warmup80):
        return systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan80Percent(course, student)
    if goalType == str(Goal.warmup90):
        return systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan90Percent(course, student)
    if goalType == str(Goal.streak10):
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken30Percent(course, student, goalType)
    if goalType == str(Goal.streak70):
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken70Percent(course, student, goalType)
    if goalType == str(Goal.streak80):
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken80Percent(course, student, goalType)
    if goalType == str(Goal.streak90):
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken90Percent(course, student, goalType)
    if goalType == str(Goal.courseBucks):
        studentReg = StudentRegisteredCourses.objects.get(studentID=student, courseID=course)
        return studentReg.virtualCurrencyAmount
    if goalType == str(Goal.courseXP):
        time_period = TimePeriods.timePeriods[1503]
        id, xp = studentScore(student, course, 0, time_period, 0, result_only=True, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, context_dict=None)
        return xp
    if goalType == str(Goal.courseBadges):
        return systemVariables.getNumberOfBadgesEarned(course, student)
    
    
    
