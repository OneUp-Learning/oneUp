from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions, StudentVirtualCurrency, StudentVirtualCurrencyRuleBased
from Students.views.utils import studentInitialContextDict
from Instructors.models import Challenges

from Badges.models import Rules, ActionArguments, VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Badges.enums import Action, ObjectTypes
from Badges.events import register_event
from Badges.enums import Event, dict_dict_to_zipped_list

from datetime import datetime
import pytz
#import logging

@login_required
def transactionsView(request):
 
    context_dict,course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    
    student = context_dict['student']
    
    register_event(Event.visitedSpendedVCpage, request, student, None)

    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)  
                
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount

    # RULE BASED VC NOT USED    
    def getVCEvents():
        events = dict_dict_to_zipped_list(Event.events,['index','displayName', 'description','isVirtualCurrencySpendRule'])  
        return [id for id, _, _, is_vc in events if is_vc]

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
        # print(Event.events[event]['displayName'])
        rules = getRulesForEvent(event)
        # print(rules)
        buyRule = getFirstBuyRule(rules)
        if buyRule is None:
            return (False, 0, None)
        else:
            return (True, getAmountFromBuyRule(buyRule), buyRule)
    
    context_dict['transactions'] = get_transactions(context_dict, course, student)
    context_dict['studentName'] = student.user.first_name + " " + student.user.last_name
    context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount

    return render(request,"Students/Transactions.html",context_dict)

@login_required
def filterTransactions(request):
    from django.http import JsonResponse
    if request.method == 'GET':
        context_dict,course = studentInitialContextDict(request)    
        student = context_dict['student']
        t_type = request.GET['transaction_type']
        transactions = get_transactions(context_dict, course, student, t_type)

    return JsonResponse({'transactions': transactions})

def get_transactions(context_dict, course, student, t_type='all'):
    from django.utils import formats, timezone

    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=course)         
    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount

    name = []
    date = []
    description = []
    status = []
    total = []
    transactionID = []
    challenges = []
    transaction_type = []

    results = []
    # Show the transactions based on the type (spent, earned, or all)
    if t_type == 'spent' or t_type == 'all':
        # Get all the student spending transactions (items they bought)
        transactions = StudentVirtualCurrencyTransactions.objects.filter(student = student, course = course).filter(studentEvent__event=Event.spendingVirtualCurrency).order_by('-studentEvent__timestamp')

        for transaction in transactions:
            # rule = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=False, courseID=course, vcRuleID=transaction.studentEvent.objectID).first()
            # if rule:
            #     name.append(rule.vcRuleName)
            #     description.append(rule.vcRuleDescription)
            #     date.append(transaction.studentEvent.timestamp)
            #     total.append(rule.vcRuleAmount)
            #     status.append(transaction.status)
            #     transactionID.append(transaction.transactionID)
            #     transaction_type.append("Purchase")
            #     # Show what challenge the transaction was for
            #     if transaction.objectType == ObjectTypes.challenge:
            #         challenge = Challenges.objects.filter(courseID = course, challengeID = transaction.objectID).first()
            #         if challenge:
            #             challenges.append(challenge.challengeName)
            #         else:
            #             challenges.append(None)
            #     else:
            #         challenges.append(None)

            
            name.append(transaction.name)
            description.append(transaction.description)
            date.append(transaction.studentEvent.timestamp)
            total.append(transaction.amount)
            status.append(transaction.status)
            transactionID.append(transaction.transactionID)
            transaction_type.append("Purchase")
            # Show what challenge the transaction was for
            if transaction.objectType == ObjectTypes.challenge:
                challenge = Challenges.objects.filter(courseID = course, challengeID = transaction.objectID).first()
                if challenge:
                    challenges.append(challenge.challengeName)
                else:
                    challenges.append(None)
            else:
                challenges.append(None)

    if t_type == 'earned' or t_type == 'all':
        # Get all the transactions that the student has earned 
        stud_vc =  StudentVirtualCurrency.objects.filter(courseID=course,studentID=student).order_by('-timestamp') 
        for stud_VCrule in stud_vc:
            # If the transaction has a rule attached, get the information from that rule
            if hasattr(stud_VCrule, 'studentvirtualcurrencyrulebased'):
                vcrule = stud_VCrule.studentvirtualcurrencyrulebased.vcRuleID
                if not vcrule:
                    continue
                if stud_VCrule.courseID == course and vcrule.vcRuleType:
                    name.append(vcrule.vcRuleName)
                    description.append(vcrule.vcRuleDescription)
                    date.append(stud_VCrule.timestamp)
                    
                    if vcrule.vcRuleAmount != -1:
                        total.append(stud_VCrule.value)
                    else:
                        avcr = VirtualCurrencyRuleInfo.objects.filter(vcRuleID=vcrule.vcRuleID).first()
                        if avcr:
                            if (ActionArguments.objects.filter(ruleID=avcr.ruleID).exists()):
                                total.append(ActionArguments.objects.get(ruleID=avcr.ruleID).argumentValue)
                            else:
                                total.append(0)   
                        else:
                            total.append(stud_VCrule.value)
            else:
                name.append(stud_VCrule.vcName)
                description.append(stud_VCrule.vcDescription)
                date.append(stud_VCrule.timestamp)
                total.append(stud_VCrule.value)

            status.append("Complete")
            transaction_type.append("Earned")
            transactionID.append(None)
            challenges.append(None)
            
    # Sort by status (Request -> In Progress -> Complete)
    transactions = sorted(zip(transactionID, name,description,date, total, status, challenges, transaction_type), key=lambda s : (s[5], s[3]), reverse=True)
    
    # Need to format the datetime object to be like it shows in the html file
    # This will mimick what django does to render dates on the frontend
    # Since the data is being returned as JSON for filtering
    transactions_formatted = []
    for transaction in transactions:
        tuple_list = list(transaction)
        time = tuple_list[3].replace(tzinfo=pytz.UTC)   
        tuple_list[3] = formats.date_format(time.astimezone(timezone.get_current_timezone()), "DATETIME_FORMAT")
        transactions_formatted.append(tuple_list)
    return transactions_formatted