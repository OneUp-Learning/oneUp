'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render


from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict
from Badges.models import VirtualCurrencyPeriodicRule
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_variable, delete_periodic_task
from django.shortcuts import redirect
from Students.models import StudentRegisteredCourses
import random

@login_required
def timeBasedVirtualCurrencyView(request):
 
    context_dict,current_course = initialContextDict(request);
        
    if request.GET:    
        # Getting the currency information which has been selected
        if 'vcRuleID' in request.GET:    
            if request.GET['vcRuleID']:
                vcId = request.GET['vcRuleID']
                periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=vcId)
                # The range part is the index numbers.  
                context_dict = createTimePeriodContext(context_dict) 
                context_dict['vc'] = periodicVC
        return render(request,'Badges/TimeBasedVirtualCurrency.html', context_dict)
        
    if request.POST:
        if 'delete' in request.POST:
            vc = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=request.POST['vcRuleID'])
            delete_periodic_task(vc.periodicVariableID, current_course, vc.timePeriodID, number_of_top_students= vc.numberOfAwards, badge_id=vc.vcRuleID)
            VirtualCurrencyPeriodicRule.objects.get(vcRuleID=request.POST['vcRuleID']).delete()
            return redirect('PeriodicVirtualCurrencyEarnRuleList.html')
    
        if 'edit' in request.POST:
            # Edit badge
            delete_periodic_task(request.POST['periodicVariableSelected'], current_course, request.POST['timePeriodSelected'], number_of_top_students=request.POST['ranking'], badge_id=request.POST['badgeId'])
            periodicVC = VirtualCurrencyPeriodicRule.objects.get(vcRuleID=request.POST['vcRuleID'])
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
                periodicVC.periodicVariableID = request.POST['periodicVariableSelected']
                periodicVC.timePeriodID = request.POST['timePeriodSelected']
                selection = request.POST['selection']
                
                if selection == "TopN":
                    periodicVC.numberOfAwards = int(request.POST['numberOfAwards'])
                if selection == "All":
                    count = StudentRegisteredCourses.objects.filter(courseID=current_course).count()
                    periodicVC.numberOfAwards = count
                    request.POST['numberOfAwards'] = count
                if selection == "Random":
                    periodicVC.numberOfAwards = random.randint(1,request.POST['numberOfAwards'])
                    request.POST['numberOfAwards'] = periodicVC.numberOfAwards
                    
                
                periodicVC.save()
                
                setup_periodic_variable(int(periodicVC.vcRuleID), int(request.POST['periodicVariableSelected']), current_course, int(request.POST['timePeriodSelected']), number_of_top_students=int(request.POST['numberOfAwards']), badge_id=periodicVC.vcRuleID)                 
            return render(request,'Badges/PeriodicVirtualCurrencyEarnRuleList.html', context_dict)
    context_dict = createTimePeriodContext(context_dict) 
    
    return render(request,'Badges/TimeBasedVirtualCurrency.html', context_dict)

def createTimePeriodContext(context_dict):

    context_dict['periodicVariables'] = [v for _, v in PeriodicVariables.periodicVariables.items()]
    context_dict['timePeriods'] = [t for _, t in TimePeriods.timePeriods.items()]
    return context_dict