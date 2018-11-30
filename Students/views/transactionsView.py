from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions
from Students.views.utils import studentInitialContextDict
from Instructors.models import Challenges

from Badges.models import Rules, ActionArguments, VirtualCurrencyRuleInfo
from Badges.enums import Action, ObjectTypes
from Badges.events import register_event
from Badges.enums import Event

from datetime import datetime
#import logging

@login_required
def transactionsView(request):
 
    context_dict,course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    
    student = context_dict['student']
    
    register_event(Event.visitedSpendedVCpage, request, student, None)

    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)  
                
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount         
     
    # Get all transactions for the student and send it to the webpage
#     transactions = StudentVirtualCurrencyTransactions.objects.filter(student = student, course = course).filter(studentEvent__event__in=[Event.instructorHelp, Event.buyAttempt, Event.extendDeadline, Event.dropLowestAssignGrade, Event.getDifferentProblem,
#                                                                                                         Event.seeClassAverage, Event.chooseLabPartner, Event.chooseProjectPartner, Event.uploadOwnAvatar, Event.chooseDashboardBackground,
#                                                                                                         Event.getSurpriseAward, Event.chooseBackgroundForYourName, Event.buyExtraCreditPoints]).order_by('-studentEvent__timestamp')
    transactions = StudentVirtualCurrencyTransactions.objects.filter(student = student, course = course).filter(studentEvent__event__in=[Event.instructorHelp, Event.buyAttempt, Event.extendDeadlineHW, Event.extendDeadlineLab,Event.replaceLowestAssignGrade, Event.getDifferentProblem,
                                Event.getSurpriseAward, Event.buyExtraCreditPoints, Event.buyTestTime, Event.getCreditForOneTestProblem, Event.buyMissedLab, Event.changeHWWeights, Event.examExemption]).order_by('-studentEvent__timestamp')

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
        # print(Event.events[event]['displayName'])
        rules = getRulesForEvent(event)
        # print(rules)
        buyRule = getFirstBuyRule(rules)
        if buyRule is None:
            return (False, 0, None)
        else:
            return (True, getAmountFromBuyRule(buyRule), buyRule)
        
    #logger.debug(transactions)
    name = []
    purchaseDate = []
    description = []
    status = []
    total = []
    transactionID = []
    challenges = []
    
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
        status.append(transaction.status)
        transactionID.append(transaction.transactionID)
        # Show what challenge the transaction was for
        if transaction.objectType == ObjectTypes.challenge:
            challenge = Challenges.objects.filter(courseID = course, challengeID = transaction.objectID)
            if challenge:
                challenges.append(challenge[0].challengeName)
            else:
                challenges.append(None)
        else:
            challenges.append(None)
    
    #logger.debug(transactionID)
    #logger.debug(name)
    #logger.debug(description)
    #logger.debug(purchaseDate)
    #logger.debug(total)
    
    # Sort by status (Request -> In Progress -> Complete)
    context_dict['transactions'] = sorted(zip(transactionID, name,description,purchaseDate, total, status, challenges), key=lambda s : s[5][1])
    context_dict['studentName'] = student.user.first_name + " " + student.user.last_name
    context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
    return render(request,"Students/Transactions.html",context_dict)