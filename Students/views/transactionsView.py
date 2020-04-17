from datetime import datetime, timedelta

import pytz
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from Badges.enums import Action, Event, ObjectTypes, dict_dict_to_zipped_list
from Badges.events import register_event
from Badges.models import (ActionArguments, CourseConfigParams, Rules,
                           VirtualCurrencyCustomRuleInfo,
                           VirtualCurrencyRuleInfo)
from Instructors.constants import transaction_reasons
from Instructors.models import Challenges
from Instructors.views.utils import current_localtime
from Students.models import (StudentRegisteredCourses, StudentVirtualCurrency,
                             StudentVirtualCurrencyRuleBased,
                             StudentVirtualCurrencyTransactions)
from Students.views.utils import studentInitialContextDict

#import logging


@login_required
def transactionsView(request):

    context_dict, course = studentInitialContextDict(request)
    #logger = logging.getLogger(__name__)
    # Redirects students from VC page if VC not enabled
    config = CourseConfigParams.objects.get(courseID=course)
    vcEnabled = config.virtualCurrencyUsed
    if not vcEnabled:
        return redirect('/oneUp/students/StudentCourseHome')

    student = context_dict['student']

    register_event(Event.visitedSpendedVCpage, request, student, None)

    st_crs = StudentRegisteredCourses.objects.get(
        studentID=student, courseID=course)

    currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount

    # RULE BASED VC NOT USED
    def getVCEvents():
        events = dict_dict_to_zipped_list(
            Event.events, ['index', 'displayName', 'description', 'isVirtualCurrencySpendRule'])
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
        if ActionArguments.objects.filter(ruleID=rule.ruleID, sequenceNumber=1).exists:
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

    context_dict['transactions'] = get_transactions(
        context_dict, course, student)
    context_dict['studentName'] = student.user.first_name + \
        " " + student.user.last_name
    context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
    new_transactions_ids_name = get_new_trasactions_ids_names(
        course, student)
    context_dict['new_transactions_ids_name'] = new_transactions_ids_name
    print("newly added transations", new_transactions_ids_name)
    context_dict["transaction_reasons"] = transaction_reasons
    return render(request, "Students/Transactions.html", context_dict)


@login_required
def filterTransactions(request):
    from django.http import JsonResponse
    if request.method == 'GET':
        context_dict, course = studentInitialContextDict(request)
        student = context_dict['student']
        t_type = request.GET['transaction_type']
        transactions = get_transactions(context_dict, course, student, t_type)

    return JsonResponse({'transactions': transactions})


def get_new_trasactions_ids_names(course, student):
    '''Filter the newly made transactions so we can record the reasons for the transactions'''

    timestamp_from = current_localtime() - timedelta(seconds=120)
    timestamp_to = current_localtime() + timedelta(seconds=1200)
    transactions = StudentVirtualCurrencyTransactions.objects.filter(
        student=student, course=course, transactionReason="", timestamp__gte=timestamp_from, timestamp__lt=timestamp_to)
    transactionsNames = [t.name for t in transactions]

    idsToBeDeleted = []
    for i in range(0, len(transactions)):
        if transactionsNames[i] in transactionsNames[i+1:]:
            idsToBeDeleted.append(transactions[i].transactionID)

    i = 0
    Is = []
    ids = []
    names = []
    for transaction in transactions:
        if transaction.transactionID in idsToBeDeleted:
            continue
        ids.append(transaction.transactionID)
        names.append(transaction.name)
        Is.append(i)
        i += 1
    return zip(Is, ids, names)


def save_transaction_reason(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        transaction = StudentVirtualCurrencyTransactions.objects.get(
            transactionID=int(request.POST['id']))
        transaction.transactionReason = request.POST['reason']
        transaction.save()
        timestamp_from = current_localtime() - timedelta(seconds=6220) 
        timestamp_to = current_localtime() + timedelta(seconds=1200) 
        transactions = StudentVirtualCurrencyTransactions.objects.filter(
            student=transaction.student, course=transaction.course, name=transaction.name, transactionReason="", timestamp__gte=timestamp_from, timestamp__lt=timestamp_to)
        for transaction in transactions:
            transaction.transactionReason = request.POST['reason']
            transaction.save()

    return JsonResponse({'status': "successful"})


def get_transactions(context_dict, course, student, t_type='all'):
    from django.utils import formats, timezone

    st_crs = StudentRegisteredCourses.objects.get(
        studentID=student, courseID=course)
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
        transactions = StudentVirtualCurrencyTransactions.objects.filter(student=student, course=course).filter(
            studentEvent__event=Event.spendingVirtualCurrency).order_by('-studentEvent__timestamp')

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
                challenge = Challenges.objects.filter(
                    courseID=course, challengeID=transaction.objectID).first()
                if challenge:
                    challenges.append(challenge.challengeName)
                else:
                    challenges.append(None)
            else:
                challenges.append(None)

    if t_type == 'earned' or t_type == 'all':
        # Get all the transactions that the student has earned
        stud_vc = StudentVirtualCurrency.objects.filter(
            courseID=course, studentID=student).order_by('-timestamp')
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
                        avcr = VirtualCurrencyRuleInfo.objects.filter(
                            vcRuleID=vcrule.vcRuleID).first()
                        if avcr:
                            if (ActionArguments.objects.filter(ruleID=avcr.ruleID).exists()):
                                total.append(ActionArguments.objects.get(
                                    ruleID=avcr.ruleID).argumentValue)
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

    # Sort by status (Request -> In Progress -> Complete) then datetime
    status_order = ['Complete', 'Reverted', 'In Progress', 'Requested']
    transactions = sorted(zip(transactionID, name, description, date, total, status,
                              challenges, transaction_type), key=lambda s: (status_order.index(s[5]), s[3]), reverse=True)

    # Need to format the datetime object to be like it shows in the html file
    # This will mimick what django does to render dates on the frontend
    # Since the data is being returned as JSON for filtering
    transactions_formatted = []
    for transaction in transactions:
        tuple_list = list(transaction)
        time = tuple_list[3].replace(tzinfo=pytz.UTC)
        tuple_list[3] = formats.date_format(time.astimezone(
            timezone.get_current_timezone()), "DATETIME_FORMAT")
        transactions_formatted.append(tuple_list)
    return transactions_formatted
