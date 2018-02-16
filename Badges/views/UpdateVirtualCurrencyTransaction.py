from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Students.models import StudentVirtualCurrencyTransactions
from Badges.models import ActionArguments, Action, Rules
from Badges.enums import Event
from datetime import datetime
#import logging

@login_required
def updateVirtualCurrencyTransaction(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        #logger = logging.getLogger(__name__)
        
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
            
        if request.method == 'GET':
            if 'transactionID' in request.GET:
                # Get the transaction data and send it to the page
                transaction = StudentVirtualCurrencyTransactions.objects.get(pk=int(request.GET['transactionID']))

                event = Event.events[transaction.studentEvent.event]
                context_dict['name'] = event['displayName']
                context_dict['description'] = event['description']
                context_dict['purchaseDate'] = transaction.studentEvent.timestamp
                context_dict['total'] = getBuyAmountForEvent(transaction.studentEvent.event)[1]
                context_dict['student'] = transaction.student
                context_dict['status'] = transaction.status
                context_dict['instructorNote'] = transaction.instructorNote
                context_dict['noteForStudent'] = transaction.noteForStudent
                context_dict['transactionID'] = request.GET['transactionID']
                #logger.debug(context_dict)
                
            return render(request, 'Badges/UpdateVirtualCurrencyTransaction.html', context_dict)
        elif request.method == 'POST':
            if 'transactionID' in request.POST:
                # Save the transaction status and notes
                transaction = StudentVirtualCurrencyTransactions.objects.get(pk=int(request.POST['transactionID']))
                
                transaction.status = request.POST['updateStatus']
                transaction.instructorNote = request.POST['instructorNotes']
                transaction.noteForStudent = request.POST['studentNotes']
                transaction.save()
                
            return redirect('VirtualCurrencyTransactions.html')
                