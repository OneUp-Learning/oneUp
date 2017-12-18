from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions
from Students.views.utils import studentInitialContextDict

from Badges.models import Rules, ActionArguments
from Badges.enums import Action, Event
from datetime import datetime
#import logging

@login_required
def transactionNotesView(request):
 
    context_dict,course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    
    student = context_dict['student']
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)  
                
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount         
     
    # Code from virtual currency shop view
    def getRulesForEvent(event):
        return Rules.objects.filter(ruleevents__event=event, courseID=course)

    # We assume that if a rule decreases virtual currency, it is a
    # buy rule.  This function assumes that virtual currency penalty
    # rules have already been screened out.  A more robust test
    # would be needed if used in a different context.        
    def checkIfRuleIsBuyRule(rule):
        return rule.actionID == Action.decreaseVirtualCurrency
    
    def getAmountFromBuyRule(rule):
        return int(ActionArguments.objects.get(ruleID=rule, sequenceNumber=1).argumentValue)
    
    # We just find the first one.  This should generally be fine
    # since there should be at most one.
    def getFirstBuyRule(ruleList):
        for rule in ruleList:
            if checkIfRuleIsBuyRule(rule):
                return rule
        return None
    
    def getBuyAmountForEvent(event):
        rules = getRulesForEvent(event)
        buyRule = getFirstBuyRule(rules)
        if buyRule is None:
            return (False, 0)
        else:
            return (True, getAmountFromBuyRule(buyRule))
        
    transaction = StudentVirtualCurrencyTransactions.objects.get(pk=int(request.GET['transactionID']))
    
    event = Event.events[transaction.studentEvent.event]
    context_dict['name'] = event['displayName']
    context_dict['description'] = event['description']
    context_dict['purchaseDate'] = datetime.strptime(str(transaction.studentEvent.timestamp), "%Y-%m-%d %H:%M:%S.%f+00:00").strftime("%m/%d/%Y %I:%M %p")
    context_dict['total'] = getBuyAmountForEvent(transaction.studentEvent.event)[1]
    context_dict['status'] = transaction.status
    context_dict['noteForStudent'] = transaction.noteForStudent
    
    #logger.debug(context_dict)

    context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
    return render(request,"Students/TransactionNotes.html",context_dict)