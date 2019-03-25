#
# Created on  2/18/2019
# James Cherry
#Modeled after announcementCreateView.py
#
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.utils import utcDate, initialContextDict

#2.18.2019 JC
from Students.models import StudentGoalSetting
from Badges.enums import Goal
from Badges import systemVariables
from Students.views.utils import studentInitialContextDict
from Badges.systemVariables import SystemVariable
from django.template.context_processors import request

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
        goal.progressToGoal = (goalProgressFxn(goal.goalType, goal.courseID, goal.studentID) / goal.targetedNumber) * 100       
        
        goal.save();  #Writes to database.    
                
        return redirect('GoalsList')

    ######################################
    # request.GET 
    else:
        if request.GET:
                            
            # If studentGoalId is specified then we load for editing.
            if 'studentGoalID' in request.GET:
                goal = StudentGoalSetting.objects.get(pk=int(request.GET['studentGoalID']))
                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['studentGoalID'] = request.GET['studentGoalID']
                context_dict['goalType'] = goal.goalType
                context_dict['targetedNumber'] = goal.targetedNumber
                                

    return render(request,'Students/GoalsCreationForm.html', context_dict)

def goalProgressFxn(goalType, course, student):
    sysVarFxn = systemVariables
    sysVar = systemVariables.SystemVariable
    
    if goalType == 1600:
        return int(systemVariables.getNumberOfUniqueWarmupChallengesAttempted(course, student))
    if goalType == 1602:
        return int(systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan70Percent(course, student))
    if goalType == 1604:
        return int(systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan80Percent(course, student))
    if goalType == 1606:
        return int(systemVariables.getNumberOfUniqueWarmupChallengesGreaterThan90Percent(course, student))
    if goalType == 1610:
        return int(systemVariables.getConsecutiveDaysWarmUpChallengesTaken30Percent(course, student, goalType))
    if goalType == 1612:
        return int(systemVariables.getConsecutiveDaysWarmUpChallengesTaken70Percent(course, student, goalType))
    if goalType == 1614:
        return int(systemVariables.getConsecutiveDaysWarmUpChallengesTaken80Percent(course, student, goalType))
    if goalType == 1616:
        return int(systemVariables.getConsecutiveDaysWarmUpChallengesTaken90Percent(course, student, goalType))
    if goalType == 1640:
        return int(systemVariables.getNumberOfBadgesEarned(course, student))
    
    
    
