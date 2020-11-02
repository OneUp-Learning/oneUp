'''
Created on Oct 23, 2019

@author: cmickle
'''
import pprint

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from Instructors.views import utils
from oneUp.decorators import instructorsCheck

pp = pprint.PrettyPrinter(indent=4)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def teamListView(request):
    context_dict,currentCourse = utils.initialContextDict(request)

    return render(request,'Instructors/teamList.html', context_dict)