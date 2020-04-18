'''
Created on 2/18/2019

Modeled after announcementCreateView.py

@author: jcherry
'''

import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from Badges.enums import ObjectTypes
from Badges.periodicVariables import PeriodicVariables
from Badges.systemVariables import SystemVariable
from Badges.tasks import create_goal_expire_event
from Instructors.views.debugSysVars import getSysValues
from Instructors.views.utils import current_localtime
from Students.models import StudentGoalSetting, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def goal_view(request):
 
    context_dict, current_course = studentInitialContextDict(request)

    context_dict['goal_variables'] = [sysvar for i, sysvar in SystemVariable.systemVariables.items() if sysvar['studentGoal'] == True] \
                                    + [PeriodicVariables.periodicVariables[PeriodicVariables.xp_ranking]]
                                    
    print(context_dict['goal_variables'])
    if request.method == 'POST':

        if 'goal_id' in request.POST:
            goal = StudentGoalSetting.objects.get(pk=int(request.POST['goal_id']))

            if 'delete' in request.POST:
                goal.delete()
                return redirect('goalslist')
        else:
            goal = StudentGoalSetting()
        
        goal.courseID = current_course
        goal.studentID = context_dict['student']
        goal.goalType = request.POST['goal_variable']
        goal.targetedNumber = request.POST['goal_target']
        goal.timestamp = current_localtime() 
        goal.progressToGoal = process_goal(current_course, context_dict['student'], int(request.POST['goal_variable']))
        goal.recurringGoal = "recurring_goal" in request.POST
        goal.save()  

        create_goal_expire_event(request, context_dict['student'].pk, goal.pk, goal.timestamp + timedelta(days=7), request.session['django_timezone'])
                
        return redirect('goalslist')

    elif request.method == 'GET':
                
        if 'goal_id' in request.GET:
            goal = StudentGoalSetting.objects.get(pk=int(request.GET['goal_id']))

            context_dict['goal_id'] = request.GET['goal_id']
            context_dict['goal_variable'] = goal.goalType
            context_dict['goal_target'] = goal.targetedNumber
            context_dict['recurring_goal'] = goal.recurringGoal                      

    return render(request,'Students/GoalsCreationForm.html', context_dict)

def process_goal(course, student, var):
    result = getSysValues(student, var, ObjectTypes.none, course)[0][4]
    return result
