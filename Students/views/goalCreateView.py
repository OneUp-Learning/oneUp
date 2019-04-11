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
        goal.targetedNumber = int(request.POST['targetedNumber'])
        goal.timestamp = utcDate()
          
        goal.progressToGoal = goalProgressFxn(goal.goalType, goal.courseID, goal.studentID)     
        
        goal.save();  #Writes to database.    
                
        return redirect('GoalsList')

    ######################################
    # request.GET 
    else:
        if request.GET:
                            
            # If studentGoalId is specified then we load for editing.
            if 'studentGoalID' in request.GET:
                goal = StudentGoalSetting.objects.get(pk=int(request.GET['studentGoalID']))
                genums = Goal.goals
                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['studentGoalID'] = request.GET['studentGoalID']
                context_dict['goalType'] = genums[goal.goalType].get('displayName')
                context_dict['targetedNumber'] = goal.targetedNumber
                                

    return render(request,'Students/GoalsCreationForm.html', context_dict)

def goalProgressFxn(goalType, course, student):
    print (goalType)    
    if goalType == Goal.warmup10:
        return systemVariables.getNumberOfUniqueWarmupChallengesAttempted(course, student)
    if goalType == Goal.warmup70:
        return systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan70Percent(course, student)
    if goalType == Goal.warmup80:
        return systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan80Percent(course, student)
    if goalType == Goal.warmup90:
        return systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan90Percent(course, student)
    if goalType == Goal.streak10:
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken30Percent(course, student, goalType)
    if goalType == Goal.streak70:
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken70Percent(course, student, goalType)
    if goalType == Goal.streak80:
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken80Percent(course, student, goalType)
    if goalType == Goal.streak90:
        return systemVariables.getConsecutiveDaysWarmUpChallengesTaken90Percent(course, student, goalType)
    if goalType == Goal.courseBucks:
        studentReg = StudentRegisteredCourses.objects.get(studentID=student, courseID=course)
        return studentReg.virtualCurrencyAmount
    if goalType == Goal.courseXP:
        time_period = TimePeriods.timePeriods[1503]
        s_id, xp = studentScore(student, course, 0, time_period, 0, result_only=True, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, context_dict=None)
        return xp
    if goalType == Goal.courseBadges:
        return systemVariables.getNumberOfBadgesEarned(course, student)
    
    
    
