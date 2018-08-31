from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Instructors.views.utils import initialContextDict
from Students.models import StudentVirtualCurrencyTransactions
from Badges.models import ActionArguments, Action, Rules, VirtualCurrencyRuleInfo
from Badges.enums import Event
from datetime import datetime
#import logging

@login_required
def virtualCurrencyCompletedTransactions(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        #logger = logging.getLogger(__name__)
        
        # Code from virtual currency shop view
        def getRulesForEvent(event):
            return VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, ruleID__ruleevents__event=event, courseID=course)
    
        # We assume that if a rule decreases virtual currency, it is a
        # buy rule.  This function assumes that virtual currency penalty
        # rules have already been screened out.  A more robust test
        # would be needed if used in a different context.        
        def checkIfRuleIsBuyRule(rule):
            return rule.ruleID.actionID == Action.decreaseVirtualCurrency
        
        def getAmountFromBuyRule(rule):
            if ActionArguments.objects.filter(ruleID=rule.ruleID,sequenceNumber=1).exists:
                return int(ActionArguments.objects.get(ruleID=rule.ruleID, sequenceNumber=1).argumentValue)
            else:
                return 0
        
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
                return (False, 0, None)
            else:
                return (True, getAmountFromBuyRule(buyRule), buyRule)
            
        # Get all completed student transactions by course and send it to the webpage
#         transactions = StudentVirtualCurrencyTransactions.objects.filter(course = course, status="Complete").filter(studentEvent__event__in=[Event.instructorHelp, Event.buyAttempt, Event.extendDeadline, Event.dropLowestAssignGrade, Event.getDifferentProblem,
#                                                                                                             Event.seeClassAverage, Event.chooseLabPartner, Event.chooseProjectPartner, Event.uploadOwnAvatar, Event.chooseDashboardBackground,
#                                                                                                             Event.getSurpriseAward, Event.chooseBackgroundForYourName, Event.buyExtraCreditPoints]).order_by('-studentEvent__timestamp')
        transactions = StudentVirtualCurrencyTransactions.objects.filter(course = course, status__in=["Complete", "Reverted"]).filter(studentEvent__event__in=[Event.instructorHelp, Event.buyAttempt, Event.extendDeadlineHW, Event.extendDeadlineLab,Event.replaceLowestAssignGrade, Event.getDifferentProblem,
                                                Event.getSurpriseAward, Event.buyExtraCreditPoints, Event.buyTestTime, Event.getCreditForOneTestProblem, Event.buyMissedLab, Event.changeHWWeights, Event.examExemption]).order_by('-studentEvent__timestamp')

        #logger.debug(transactions)
        name = []
        purchaseDate = []
        student = []
        description = []
        total = []
        status = []
        transactionID = []
        for transaction in transactions:
            event = Event.events[transaction.studentEvent.event]
            _, totals, rule = getBuyAmountForEvent(transaction.studentEvent.event)
            if rule:
                name.append(rule.vcRuleName)
                description.append(rule.vcRuleDescription)
            else:
                name.append(event['displayName'])
                description.append(event['description'])
            purchaseDate.append(transaction.studentEvent.timestamp)
            total.append(totals)
            student.append(transaction.student)
            status.append(transaction.status)
            transactionID.append(transaction.transactionID)
            
        #logger.debug(student)
        #logger.debug(name)
        #logger.debug(description)
        #logger.debug(purchaseDate)
        #logger.debug(total)
        
        context_dict['transactions'] = zip(transactionID, student, name,description,purchaseDate, total, status)
        return render(request, 'Badges/VirtualCurrencyCompletedTransactions.html', context_dict)
            