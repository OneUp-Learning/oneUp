from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentVirtualCurrency
from Students.views.utils import studentInitialContextDict
from Badges.models import ActionArguments, VirtualCurrencyRuleInfo

@login_required
def earnedTransactionsView(request):
 
    context_dict,course = studentInitialContextDict(request)  
    student = context_dict['student']
    
    ruleName = []
    ruleDescription = []
    ruleAmmount = []
    timeStamp = []
    
    stud_VCrules = StudentVirtualCurrency.objects.filter(studentID=student).order_by('-timestamp') 
    
    for stud_VCrule in stud_VCrules:
        vcrule = stud_VCrule.vcRuleID
        if vcrule.courseID == course:
            ruleName.append(vcrule.vcRuleName)
            ruleDescription.append(vcrule.vcRuleDescription)
            timeStamp.append(stud_VCrule.timestamp)
            if vcrule.vcRuleAmount != -1:
                ruleAmmount.append(vcrule.vcRuleAmount)
            else:
                avcr = VirtualCurrencyRuleInfo.objects.get(vcRuleID=vcrule.vcRuleID)
                if (ActionArguments.objects.filter(ruleID=avcr.ruleID).exists()):
                    ruleAmmount.append(ActionArguments.objects.get(ruleID=avcr.ruleID).argumentValue)
                else:
                    ruleAmmount.append(0)                
            
    print(len(ruleName))
    print(len(ruleDescription))
    print(len(ruleAmmount))
    print(len(timeStamp))
    
    context_dict['transactions'] = zip(range(1,len(ruleName)+1), ruleName,ruleDescription,ruleAmmount,timeStamp)

    return render(request, 'Students/EarnedTransactions.html', context_dict)
  
