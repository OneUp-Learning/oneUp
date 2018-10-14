'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render


from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict, utcDate
from Badges.models import VirtualCurrencyPeriodicRule
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_variable, delete_periodic_task
from django.shortcuts import redirect
from Students.models import StudentRegisteredCourses
import random

@login_required
def timeBasedVirtualCurrencyView(request):
 
    context_dict,current_course = initialContextDict(request)
        
    if request.method == 'GET':    
        # Getting the currency information which has been selected
        if 'vcRuleID' in request.GET:  
            if request.GET['vcRuleID']:
                vcId = request.GET['vcRuleID']
                periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=vcId, courseID=current_course)
                context_dict['vc'] = periodicVC
                context_dict['edit'] = True
        else:
            context_dict['edit'] = False
        context_dict = createTimePeriodContext(context_dict) 
        return render(request,'Badges/TimeBasedVirtualCurrency.html', context_dict)
        
    if request.method == 'POST':
        selectorMap = {
            "TopN": 0, "All": 1, "Random": 2
        }
        selectors = request.POST.get("selectors")

        if 'delete' in request.POST:
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=request.POST['vcRuleID'], courseID=current_course)
            periodicVC.delete()

        elif 'edit' in request.POST:
            # Edit badge
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=request.POST['vcRuleID'], courseID=current_course)
            # Delete the Periodic Task then recreate it
            delete_periodic_task(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), award_type="vc", course=current_course)
        
            if request.POST['vcRuleName']:
                periodicVC.vcRuleName = request.POST['vcRuleName']
                
            if request.POST['vcRuleDescription']:
                periodicVC.vcRuleDescription = request.POST['vcRuleDescription']
                periodicVC.vcRuleType = True
   
            if request.POST['vcRuleAmount']:
                periodicVC.vcRuleAmount = request.POST['vcRuleAmount']

            periodicVC.courseID = current_course
            periodicVC.isPeriodic = True
            periodicVC.periodicType = selectorMap[selectors]
            periodicVC.periodicVariableID = request.POST['periodicVariableSelected']
            periodicVC.timePeriodID = request.POST['timePeriodSelected']
            periodicVC.threshold = request.POST['threshold']
            periodicVC.operatorType = request.POST['operator']
            periodicVC.lastModified = utcDate()
            
            if selectors == "TopN":
                periodicVC.numberOfAwards = int(request.POST['numberOfAwards'])
                periodicVC.isRandom = None
            elif selectors == "Random":
                periodicVC.isRandom = True
                periodicVC.numberOfAwards = None

            periodicVC.save()
            
            # Recreate the Periodic Task based on the type
            if selectors == "TopN":
                periodicVC.periodicTask = setup_periodic_variable(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), number_of_top_students=int(periodicVC.numberOfAwards), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, virtual_currency_amount=int(periodicVC.vcRuleAmount))
            elif selectors == "Random":
                periodicVC.periodicTask = setup_periodic_variable(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, is_random=int(periodicVC.isRandom), virtual_currency_amount=int(periodicVC.vcRuleAmount))
            else:
                periodicVC.periodicTask = setup_periodic_variable(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, virtual_currency_amount=int(periodicVC.vcRuleAmount))
            periodicVC.save()
        else:
            # Create the rule
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
            periodicVC.periodicType = selectorMap[selectors]
            periodicVC.periodicVariableID = request.POST['periodicVariableSelected']
            periodicVC.timePeriodID = request.POST['timePeriodSelected']
            periodicVC.threshold = request.POST['threshold']
            periodicVC.operatorType = request.POST['operator']
                
            if selectors == "TopN":
                periodicVC.numberOfAwards = int(request.POST['numberOfAwards'])
                periodicVC.isRandom = None
            elif selectors == "Random":
                periodicVC.isRandom = True
                periodicVC.numberOfAwards = None
          
            
            periodicVC.save()

            # Create the Periodic Task based on the type
            if selectors == "TopN":
                periodicVC.periodicTask = setup_periodic_variable(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), number_of_top_students=int(periodicVC.numberOfAwards), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, virtual_currency_amount=int(periodicVC.vcRuleAmount), is_leaderboard=True)
            elif selectors == "Random":
                periodicVC.periodicTask = setup_periodic_variable(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, is_random=int(periodicVC.isRandom), virtual_currency_amount=int(periodicVC.vcRuleAmount))
            else:
                periodicVC.periodicTask = setup_periodic_variable(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, virtual_currency_amount=int(periodicVC.vcRuleAmount))
            
            periodicVC.save()

        return redirect('PeriodicVirtualCurrencyEarnRuleList.html')

def createTimePeriodContext(context_dict):

    context_dict['periodicVariables'] = [v for _, v in PeriodicVariables.periodicVariables.items()]
    context_dict['timePeriods'] = [t for _, t in TimePeriods.timePeriods.items()]
    return context_dict