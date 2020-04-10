from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Students.models import StudentVirtualCurrencyTransactions, StudentRegisteredCourses
from Badges.models import ActionArguments, Action, Rules, VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Badges.enums import Event, ObjectTypes
from datetime import datetime
from Instructors.models import Challenges, Activities
from notify.signals import notify
import json
#import logging


@login_required
def updateVirtualCurrencyTransaction(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        #logger = logging.getLogger(__name__)

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
            rules = getRulesForEvent(event)
            buyRule = getFirstBuyRule(rules)
            if buyRule is None:
                return (False, 0, None)
            else:
                return (True, getAmountFromBuyRule(buyRule), buyRule)

        if request.method == 'GET':
            if 'transactionID' in request.GET:
                # Get the transaction data and send it to the page
                transaction = StudentVirtualCurrencyTransactions.objects.get(
                    pk=int(request.GET['transactionID']))

                # RULE BASED VC NOT USED
                # event = Event.events[transaction.studentEvent.event]
                # _, total, rule = getBuyAmountForEvent(transaction.studentEvent.event)
                # if rule:
                #     context_dict['name'] = rule.vcRuleName
                #     context_dict['description'] = rule.vcRuleDescription
                # else:
                #     context_dict['name'] = event['displayName']
                #     context_dict['description'] = event['description']

                rule = VirtualCurrencyCustomRuleInfo.objects.filter(
                    vcRuleType=False, courseID=course, vcRuleID=transaction.studentEvent.objectID).first()
                context_dict['name'] = rule.vcRuleName
                context_dict['description'] = rule.vcRuleDescription
                context_dict['purchaseDate'] = transaction.studentEvent.timestamp
                context_dict['total'] = rule.vcRuleAmount
                student_name = transaction.student.user.get_full_name()
                if transaction.student.isTestStudent:
                    student_name += " (Test Student)"
                context_dict['student'] = student_name
                context_dict['status'] = transaction.status
                context_dict['instructorNote'] = transaction.instructorNote
                context_dict['noteForStudent'] = transaction.noteForStudent
                context_dict['transactionID'] = request.GET['transactionID']
                if transaction.objectType == ObjectTypes.challenge:
                    challenge = Challenges.objects.filter(
                        courseID=course, challengeID=transaction.objectID).first()
                    if challenge:
                        context_dict['assignment'] = challenge.challengeName
                    else:
                        activity = Activities.objects.filter(
                            courseID=course, activityID=transaction.objectID).first()
                        if activity:
                            context_dict['assignment'] = activity.activityName
                        else:
                            context_dict['assignment'] = None
                else:
                    context_dict['assignment'] = None
                # logger.debug(context_dict)

            return render(request, 'Badges/UpdateVirtualCurrencyTransaction.html', context_dict)
        elif request.method == 'POST':
            if 'transactionID' in request.POST:
                transaction = StudentVirtualCurrencyTransactions.objects.get(
                    pk=int(request.POST['transactionID']))
                if request.POST['updateStatus'] == 'Reverted' and transaction.status != 'Reverted':
                    student = StudentRegisteredCourses.objects.get(
                        courseID=course, studentID=transaction.student)
                    rule = VirtualCurrencyCustomRuleInfo.objects.filter(
                        vcRuleType=False, courseID=course, vcRuleID=transaction.studentEvent.objectID).first()
                    student.virtualCurrencyAmount += rule.vcRuleAmount
                    student.save()

                if transaction.status != request.POST['updateStatus']:
                    notify.send(None, recipient=transaction.student.user, actor=request.user, verb=f'{transaction.name} VC transaction status has been updated', nf_type='VC Transaction', extra=json.dumps(
                        {"course": str(course.courseID), "name": str(course.courseName), "related_link": '/oneUp/students/Transactions'}))

                # Save the transaction status and notes
                transaction.status = request.POST['updateStatus']
                transaction.instructorNote = request.POST['instructorNotes']
                transaction.noteForStudent = request.POST['studentNotes']
                transaction.save()

            return redirect('VirtualCurrencyTransactions.html')
