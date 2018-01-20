from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions, StudentEventLog, StudentVirtualCurrency
from Students.views.utils import studentInitialContextDict

from Badges.models import Rules, ActionArguments, RuleEvents, VirtualCurrencyCustomRuleInfo
from Badges.enums import Action, Event
from datetime import datetime
from symbol import except_clause
#import logging

@login_required
def earnedTransactionsView(request):
 
    context_dict,course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    
    student = context_dict['student']
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)  
                
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount         
    
    ruleName = []
    ruleDescription = []
    ruleAmmount = []
    timeStamp = []
    
    vcCustomRules = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=True) #Get the rules that a teacher has made
    
    for r in vcCustomRules: #loop through all the custom rules
            gains = StudentVirtualCurrency.objects.filter(studentID=student, vcRuleID = r) #see if the student has a gain matching that rule
            if(gains): 
                for g in gains: #for every gain add an the info need to the proper list
                    ruleName.append(r.vcRuleName)
                    ruleDescription.append(r.vcRuleDescription)
                    ruleAmmount.append(r.vcRuleAmount)
                    timeStamp.append(g.timestamp)
            else:
                print('No virtual currency gains match that query')
                
            
    print(len(ruleName))
    print(len(ruleDescription))
    print(len(ruleAmmount))
    print(len(timeStamp))
    
    context_dict['transactions'] = zip(range(1,len(ruleName)+1), ruleName,ruleDescription,ruleAmmount,timeStamp)
    return render(request, 'Students/EarnedTransactions.html', context_dict)
  
    
  #     # Get all transactions for the student and send it to the webpage
# #     transactions = StudentVirtualCurrencyTransactions.objects.filter(student = student, course = course).filter(studentEvent__event__in=[Event.increaseVirtualCurrency]).order_by('-studentEvent__timestamp')
#     
#     #Get all the events that are connected to the student
#     studentELog = StudentEventLog.objects.filter(student=student, course=course)
#         
#     #Get all the rules and the events that match
#     rEvents = RuleEvents.objects.filter()
#     
#     #List to hold all of the rules that match the student and ended up in increase of VC
#     earnedVcEvents = []
#     earnedStuentEvensts = []
#      
# #     #match the student events with the Rule Events
# #     for studentEvent in studentELog:
# #         print('Studetn Event' + str(studentEvent))
# #         for rEvent in rEvents:
# #             if (studentEvent.event == rEvent.event) and (rEvent.rule.actionID == 710): #look at rule and make sure the action matches an increase in VC
# #                 earnedStuentEvensts.append(studentEvent)
# #                 earnedVcEvents.append(rEvent)
# #                 print(rEvent.rule)
# # 
# # 
# #     print(len(earnedStuentEvensts))
# #     print(len(earnedVcEvents))
  
            
#     #match the rules we found where increases with theactions that take place
#     actions = ActionArguments.objects.filter()
#     
#     values = []
#     
#     for e in earnedVcEvents:
#         for action in actions:
#             if e.rule == action.ruleID: #if the rules match up then we know the values
#                 values.append(action.argumentValue)
#                 print(action.argumentValue)
#                 break
                
        
#     
#     # Sort by status (Request -> In Progress -> Complete)
#     context_dict['transactions'] = sorted(zip(transactionID, name,description,purchaseDate, total, status), key=lambda s : s[5][1])
#     context_dict['studentName'] = student.user.first_name + " " + student.user.last_name
#     context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount