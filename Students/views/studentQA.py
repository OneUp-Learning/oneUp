#  GGM
#  6/23/2018

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random 
from datetime import datetime

from django.shortcuts import render
from Students.models import StudentChallenges, StudentActivities
from Instructors.models import Challenges, Activities
from Instructors.constants import default_time_str
from Instructors.views.utils import utcDate
from Students.views.utils import studentInitialContextDict
from django.db.models import Q
from Students.views.utils import studentInitialContextDict
from Badges.models import CourseConfigParams
from django.contrib.auth.decorators import login_required

@login_required
def studentQA(request):
    context_dict, currentCourse = studentInitialContextDict(request) 
    
    return render(request,'Students/StudentQA.html',context_dict)