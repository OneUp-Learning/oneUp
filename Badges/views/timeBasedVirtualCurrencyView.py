'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

import glob, os

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Instructors.views.utils import initialContextDict
from Badges.models import Badges, BadgesInfo, VirtualCurrencyPeriodicRule
from django.views.decorators.http import condition
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_variable

@login_required
def timeBasedVirtualCurrencyView(request):
 
    context_dict,current_course = initialContextDict(request);
    
    
    conditions = []
        
    if 'vcRuleID' in request.GET:    
    # Getting the currency information which has been selected
        if request.GET['vcRuleID']:
            vcId = request.GET['vcRuleID']
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=vcId)
                
            # The range part is the index numbers.  
            context_dict['vc'] = periodicVC
            
    if 'vcRuleName' in request.POST:
            periodicVC = VirtualCurrencyPeriodicRule()
            
            if request.POST['vcRuleName']:
                periodicVC.vcRuleName = request.POST['vcRuleName']
                
            if request.POST['vcRuleDescription']:
                periodicVC.vcRuleDescription = request.POST['vcRuleDescription']
                periodicVC.vcRuleType = True
                        
            if request.POST['vcRuleAmount']:
                periodicVC.vcRuleAmount = request.POST['vcRuleAmount']
                periodicVC.courseID = current_course
                periodicVC.isPeriodic = True
                periodicVC.periodicVariableID = request.POST['periodicVariableSelected']
                periodicVC.timePeriodID = request.POST['timePeriodSelected']
                periodicVC.save()
                      
                
    context_dict = createTimePeriodContext(context_dict) 
    return render(request,'Badges/TimeBasedVirtualCurrency.html', context_dict)

def createTimePeriodContext(context_dict):

    context_dict['periodicVariables'] = [v for _, v in PeriodicVariables.periodicVariables.items()]
    context_dict['timePeriods'] = [t for _, t in TimePeriods.timePeriods.items()]
    return context_dict