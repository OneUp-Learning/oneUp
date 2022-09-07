'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from Students.models import PendingVirtualApplause
from Instructors.views.utils import initialContextDict
from Badges.conditions_util import setUpContextDictForConditions
from Students.views.utils import studentInitialContextDict
from Badges.systemVariables import logger

from Badges.enums import AwardFrequency, ApplauseOption
from django.http.response import HttpResponse, HttpResponseRedirect
import json

@login_required
def checkVirtualApplauseRule(request):
    
    context_dict,currentCourse = studentInitialContextDict(request)
 
    student = context_dict['student']
      
    pendList = PendingVirtualApplause.objects.filter(studentID = student)
    pend = -1
    if len(pendList)==0:
       pend = -1
    else:
      pend = pendList[0].ApplauseOption
      if(pend <= 0):
        pend = -1
        
      pendList[0].ApplauseOption = 0
      pendList[0].save()
      
    applausArr = ""   
    for x in ApplauseOption.applauseOption :         
      applausArr += "," + str(ApplauseOption.applauseOption.setdefault(x))
     
    
    return HttpResponse(str(pend),content_type = "text/plain" )
