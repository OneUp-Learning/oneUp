from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions
from Students.views.utils import studentInitialContextDict
from Instructors.models import Challenges, Activities
from Badges.models import Rules, ActionArguments, VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Badges.enums import Action, Event, ObjectTypes
from datetime import datetime
from django.utils import formats, timezone
import pytz
#import logging

@login_required
def transactionNotesView(request):

 
    context_dict,course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    
    student = context_dict['student']
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)  
                
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount         
     
    # Code from virtual currency shop view
    # RULE BASED VC NOT USED
    def getRulesForEvent(event):
        return VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, ruleID__ruleevents__event=event, courseID=course)

    # We assume that if a rule decreases virtual currency, it is a
    # buy rule.  This function assumes that virtual currency penalty
    # rules have already been screened out.  A more robust test
    # would be needed if used in a different context.   
    # RULE BASED VC NOT USED     
    def checkIfRuleIsBuyRule(rule):
        return rule.ruleID.actionID == Action.decreaseVirtualCurrency
    # RULE BASED VC NOT USED
    def getAmountFromBuyRule(rule):
        if ActionArguments.objects.filter(ruleID=rule.ruleID,sequenceNumber=1).exists:
            return int(ActionArguments.objects.get(ruleID=rule.ruleID, sequenceNumber=1).argumentValue)
        else:
            return 0
    
    # We just find the first one.  This should generally be fine
    # since there should be at most one.
    # RULE BASED VC NOT USED
    def getFirstBuyRule(ruleList):
        for rule in ruleList:
            if checkIfRuleIsBuyRule(rule):
                return rule
        return None
    # RULE BASED VC NOT USED
    def getBuyAmountForEvent(event):
        rules = getRulesForEvent(event)
        buyRule = getFirstBuyRule(rules)
        if buyRule is None:
            return (False, 0, None)
        else:
            return (True, getAmountFromBuyRule(buyRule), buyRule)
        
    transaction = StudentVirtualCurrencyTransactions.objects.get(pk=int(request.GET['transactionID']))
    
    # RULE BASED VC NOT USED
    # event = Event.events[transaction.studentEvent.event]
    # _, total, rule = getBuyAmountForEvent(transaction.studentEvent.event)
    # if rule:
    #     context_dict['name'] = rule.vcRuleName
    #     context_dict['description'] = rule.vcRuleDescription
    # else:
    #     context_dict['name'] = event['displayName']
    #     context_dict['description'] = event['description']

    rule = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=False, courseID=course, vcRuleID=transaction.studentEvent.objectID).first()
    context_dict['name'] = transaction.name
    context_dict['description'] = transaction.description
    # Need to format the datetime object to be like it shows in the html file
    # This will mimick what django does to render dates on the frontend
    # Since the data is being returned as JSON for filtering
    time = transaction.studentEvent.timestamp.replace(tzinfo=pytz.UTC)    
    context_dict['purchaseDate'] = formats.date_format(time.astimezone(timezone.get_current_timezone()), "DATETIME_FORMAT")
    context_dict['total'] = transaction.amount
    context_dict['status'] = transaction.status
    context_dict['noteForStudent'] = transaction.noteForStudent

    if transaction.objectType == ObjectTypes.challenge:
        challenge = Challenges.objects.filter(courseID = course, challengeID = transaction.objectID).first()
        if challenge:
            context_dict['assignment'] = challenge.challengeName
        else:
            activity = Activities.objects.filter(courseID = course, activityID = transaction.objectID).first()
            if activity:
                context_dict['assignment'] = activity.activityName
            else:
                context_dict['assignment'] = None
    else:
        context_dict['assignment'] = None
    
    #logger.debug(context_dict)

    context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
    return render(request,"Students/TransactionNotes.html",context_dict)