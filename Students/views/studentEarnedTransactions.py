from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentVirtualCurrency, StudentVirtualCurrencyRuleBased
from Students.views.utils import studentInitialContextDict
from Badges.models import ActionArguments, VirtualCurrencyRuleInfo
from Badges.events import register_event
from Badges.enums import Event

@login_required
def earnedTransactionsView(request):
 
    context_dict,course = studentInitialContextDict(request)  
    student = context_dict['student']

    register_event(Event.visitedEarnedVCpage, request, student, None)
     
    ruleName = []
    ruleDescription = []
    ruleAmmount = []
    timeStamp = []
    
    stud_vc =  StudentVirtualCurrency.objects.filter(courseID=course,studentID=student).order_by('-timestamp') 
    for stud_VCrule in stud_vc:
        if hasattr(stud_VCrule, 'studentvirtualcurrencyrulebased'):
            vcrule = stud_VCrule.studentvirtualcurrencyrulebased.vcRuleID
            if stud_VCrule.courseID == course and vcrule.vcRuleType:
                ruleName.append(vcrule.vcRuleName)
                ruleDescription.append(vcrule.vcRuleDescription)
                timeStamp.append(stud_VCrule.timestamp)
                if vcrule.vcRuleAmount != -1:
                    ruleAmmount.append(stud_VCrule.value)
                else:
                    avcr = VirtualCurrencyRuleInfo.objects.get(vcRuleID=vcrule.vcRuleID)
                    if (ActionArguments.objects.filter(ruleID=avcr.ruleID).exists()):
                        ruleAmmount.append(ActionArguments.objects.get(ruleID=avcr.ruleID).argumentValue)
                    else:
                        ruleAmmount.append(0)   
        else:
            ruleName.append(stud_VCrule.vcName)
            ruleDescription.append(stud_VCrule.vcDescription)
            timeStamp.append(stud_VCrule.timestamp)
            ruleAmmount.append(stud_VCrule.value)

            
    print(ruleName)
    
    context_dict['transactions'] = zip(range(1,len(ruleName)+1), ruleName,ruleDescription,ruleAmmount,timeStamp)

    return render(request, 'Students/EarnedTransactions.html', context_dict)
  
