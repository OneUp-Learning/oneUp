'''
Created on 4/4/2019

Based on classAchievementsVizView.py as a template

@author: James Cherry
'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Challenges, CoursesSkills
from Instructors.views.utils import initialContextDict
from Students.models import StudentChallenges, StudentCourseSkills, StudentRegisteredCourses
from oneUp.decorators import instructorsCheck 

from Students.models import StudentGoalSetting
from Students.views.utils import studentInitialContextDict 
from Students.models import StudentGoalSetting
from Badges.enums import Goal
from Badges import systemVariables
from Students.views import goalCreateView, goalsListView
    
def classGoalsViz(request):

    context_dict, currentCourse = studentInitialContextDict(request)
    
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)                
    students = []                                         
    for st_c in st_crs:
        students.append(st_c.studentID)
        
    allChallengGrades = []
                            
        #Displaying the list of challenges from database
        0)