'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render


from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict, utcDate
from Badges.models import VirtualCurrencyPeriodicRule
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_vc, delete_periodic_task
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
                if periodicVC.periodicVariableID == 1408 or periodicVC.periodicVariableID == 1407:
                    context_dict['checkbox'] = periodicVC.resetStreak
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
        else:

            if 'edit' in request.POST:
                # Edit badge
                periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=request.POST['vcRuleID'], courseID=current_course)
            else:
                periodicVC = VirtualCurrencyPeriodicRule()
                
            if request.POST['vcRuleName']:
                periodicVC.vcRuleName = request.POST['vcRuleName']
                
            if request.POST['vcRuleDescription']:
                periodicVC.vcRuleDescription = request.POST['vcRuleDescription']
                periodicVC.vcRuleType = True
   
            if request.POST['vcRuleAmount']:
                periodicVC.vcRuleAmount = request.POST['vcRuleAmount']
                
            if 'resetStreak' in request.POST:
                if int(request.POST['resetStreak']):
                    periodicVC.resetStreak = True
                else:
                    periodicVC.resetStreak = False
                
            periodicVC.courseID = current_course
            periodicVC.isPeriodic = True
            
            periodicVC.periodicVariableID = request.POST['periodicVariableSelected']
            periodicVC.timePeriodID = request.POST['timePeriodSelected']
            periodicVC.threshold = request.POST['threshold']
            periodicVC.operatorType = request.POST['operator']
            periodicVC.lastModified = utcDate()
            
            if 'selectors' in request.POST:
                periodicVC.periodicType = selectorMap[selectors]
                if selectors == "TopN":
                    periodicVC.numberOfAwards = int(request.POST['numberOfAwards'])
                    periodicVC.isRandom = None
                elif selectors == "Random":
                    periodicVC.isRandom = True
                    periodicVC.numberOfAwards = None

            periodicVC.save()

            # if it has a periodic task Delete the Periodic Task then recreate it
            if periodicVC.periodicTask:
                periodicVC.periodicTask.delete()
            # delete_periodic_task(unique_id=int(periodicVC.vcRuleID), variable_index=int(periodicVC.periodicVariableID), award_type="vc", course=current_course)
            
            # Recreate the Periodic Task based on the type
            if selectors == "TopN":
                periodicVC.periodicTask = setup_periodic_vc(unique_id=int(periodicVC.vcRuleID), virtual_currency_amount=int(periodicVC.vcRuleAmount), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), number_of_top_students=int(periodicVC.numberOfAwards), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType)
            elif selectors == "Random":
                periodicVC.periodicTask = setup_periodic_vc(unique_id=int(periodicVC.vcRuleID), virtual_currency_amount=int(periodicVC.vcRuleAmount), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType, is_random=int(periodicVC.isRandom))
            else:
                periodicVC.periodicTask = setup_periodic_vc(unique_id=int(periodicVC.vcRuleID), virtual_currency_amount=int(periodicVC.vcRuleAmount), variable_index=int(periodicVC.periodicVariableID), course=current_course, period_index=int(periodicVC.timePeriodID), threshold=int(periodicVC.threshold), operator_type=periodicVC.operatorType)
            periodicVC.save()

        return redirect('PeriodicVirtualCurrencyEarnRuleList.html')

def createTimePeriodContext(context_dict):

    context_dict['periodicVariables'] = [v for _, v in PeriodicVariables.periodicVariables.items()]
    context_dict['timePeriods'] = [t for _, t in TimePeriods.timePeriods.items()]
    return context_dict