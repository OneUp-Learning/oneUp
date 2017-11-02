from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentEventLog, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict

from Badges.models import Rules, ActionArguments
from Badges.enums import Action, Event
from datetime import datetime
#import logging

@login_required
def transactionsView(request):
 
    context_dict,course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    
    student = context_dict['student']
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)  
                
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount         
     
    transactions = StudentEventLog.objects.filter(student = student, course = course).filter(event__in=[Event.buyHint, Event.buyAttempt, Event.extendDeadline, Event.dropLowestAssignGrade, Event.getDifferentProblem,
                                                                                                        Event.seeClassAverage, Event.chooseLabPartner, Event.chooseProjectPartner, Event.uploadOwnAvatar, Event.chooseDashboardBackground,
                                                                                                        Event.getSurpriseAward, Event.chooseBackgroundForYourName]).order_by('-timestamp')
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
        # print(Event.events[event]['displayName'])
        rules = getRulesForEvent(event)
        # print(rules)
        buyRule = getFirstBuyRule(rules)
        if buyRule is None:
            return (False, 0)
        else:
            return (True, getAmountFromBuyRule(buyRule))
        
    #logger.debug(transactions)
    name = []
    purchaseDate = []
    description = []
    total = []
    
    for transaction in transactions:
        event = Event.events[transaction.event]
        name.append(event['displayName'])
        description.append(event['description'])
        purchaseDate.append(datetime.strptime(str(transaction.timestamp), "%Y-%m-%d %H:%M:%S.%f+00:00").strftime("%m/%d/%Y %I:%M %p"))
        total.append(getBuyAmountForEvent(transaction.event)[1])
        
    #logger.debug(name)
    #logger.debug(description)
    #logger.debug(purchaseDate)
    #logger.debug(total)
    
    context_dict['transactions'] = zip(name,description,purchaseDate, total)
    context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
    return render(request,"Students/Transactions.html",context_dict)