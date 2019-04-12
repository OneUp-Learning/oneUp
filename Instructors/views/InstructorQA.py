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
from Instructors.views.utils import initialContextDict
from django.db.models import Q


from django.contrib.auth.decorators import login_required

@login_required
def instructorQA(request):
    context_dict, currentCourse = initialContextDict(request)          
    return render(request,'instructors/InstructorQA.html',context_dict)