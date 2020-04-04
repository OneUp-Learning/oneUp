'''
Created on 4/1/2019

Modeled after instructors/deleteView

@author: jcherry
'''

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from Students.models import Student, StudentRegisteredCourses
from Instructors.models import Questions, Courses, Challenges, Skills, ChallengesQuestions, Topics, CoursesSubTopics, Announcements, Activities, Milestones
from Instructors.constants import unassigned_problems_challenge_name
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck  
from Badges.models import VirtualCurrencyCustomRuleInfo

from Students.models import StudentGoalSetting
from Badges.enums import Goal
from Badges import systemVariables
from Students.views.utils import studentInitialContextDict
from Badges.systemVariables import SystemVariable
from django.template.context_processors import request

@login_required
def deleteStudentGoal(request):
 
    context_dict, currentCourse = studentInitialContextDict(request)

    if request.POST:

        try:
            if request.POST['studentGoalID']:
                sgi = request.POST['studentGoalID']
                goal = StudentGoalSetting.objects.get(pk=int(sgi))           
                message = "Student Goal: "+str(goal.studentGoalID)+ " created by "+str(goal.studentID)+ " for " + str(goal.courseID) + " on " + str(goal.timestamp) + "was successfully deleted"
                goal.delete()
        except StudentGoalSetting.DoesNotExist:
            message = "There was a problem deleting Student Goal ID #"+str(goal.studentGoalID)

        context_dict['message']=message
        
    return redirect('/oneUp/students/GoalsList', context_dict)