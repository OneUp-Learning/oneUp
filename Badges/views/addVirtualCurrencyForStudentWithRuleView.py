from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict, current_localtime
from Instructors.constants import unspecified_vc_manual_rule_name, unspecified_vc_manual_rule_description
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo, BadgesVCLog
from Students.models import StudentRegisteredCourses, Student, StudentVirtualCurrencyRuleBased, StudentVirtualCurrency, StudentVirtualCurrencyTransactions
from Badges.systemVariables import logger
from notify.signals import notify
import json
from Badges.events import register_event
from Badges.enums import Event
from Instructors.views.whoAddedVCAndBadgeView import create_badge_vc_log_json


@login_required
def addVirtualCurrencyForStudentWithRuleView(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        if request.method == 'GET':
            students = StudentRegisteredCourses.objects.filter(
                courseID=course).order_by("studentID__user__last_name")
            studentID = []
            studentName = []
            studentCurrencyVC = []
            test_student_info = []
            for studentobj in students:
                if studentobj.studentID.isTestStudent:
                    test_student_info.append(
                        (studentobj.studentID, f'(Test Student) {studentobj.studentID.user.get_full_name()}', studentobj.virtualCurrencyAmount))
                else:
                    studentID.append(studentobj.studentID)
                    studentName.append(
                        studentobj.studentID.user.get_full_name())
                    studentCurrencyVC.append(studentobj.virtualCurrencyAmount)

            rules = VirtualCurrencyCustomRuleInfo.objects.filter(
                courseID=course)
            customRules = [r for r in rules if not hasattr(
                r, 'virtualcurrencyruleinfo')]

            allRulesID = []
            allRulesName = []
            allRulesAmount = []
            for rule in customRules:
                allRulesID.append(rule.vcRuleID)
                allRulesName.append(rule.vcRuleName)
                allRulesAmount.append(rule.vcRuleAmount)

            # insert the test student info last
            test_student_info = sorted(
                test_student_info, key=lambda x: x[1].casefold())
            for ID, name, vc in test_student_info:
                studentID.append(ID)
                studentName.append(name)
                studentCurrencyVC.append(vc)

            # , key=lambda tup: tup[1])
            context_dict['students'] = list(
                zip(studentID, studentName, studentCurrencyVC))

            context_dict['rules'] = list(
                zip(allRulesID, allRulesName, allRulesAmount))

            # Create default manual earning rule if it doesn't exist in this course
            if not VirtualCurrencyCustomRuleInfo.objects.filter(courseID=course, vcRuleName=unspecified_vc_manual_rule_name, vcRuleAmount=-1, vcRuleType=True).exists():
                manual_earning_rule = VirtualCurrencyCustomRuleInfo()
                manual_earning_rule.courseID = course
                manual_earning_rule.vcRuleName = unspecified_vc_manual_rule_name
                manual_earning_rule.vcRuleType = True
                manual_earning_rule.vcRuleDescription = unspecified_vc_manual_rule_description
                manual_earning_rule.vcRuleAmount = -1
                manual_earning_rule.vcAmountVaries = True
                manual_earning_rule.save()

            return render(request, 'Badges/AddVirtualCurrency.html', context_dict)
        elif request.method == 'POST':
            logger.debug(request.POST)
            students = StudentRegisteredCourses.objects.filter(courseID=course)

            for studentobj in students:
                studentValAttribute = str(studentobj.studentID) + '_Value'
                studentRuleAttribute = str(studentobj.studentID) + '_Rule'
                accumulative_type = request.POST.get(
                    str(studentobj.studentID) + '_type')

                if request.POST[studentValAttribute] == '' or request.POST[studentRuleAttribute] == '':
                    continue

                # Virtual currency should be positive
                vcAmount = int(request.POST[studentValAttribute])
                if vcAmount < 0:
                    vcAmount = 0
                prev_amount = studentobj.virtualCurrencyAmount
                if accumulative_type == 'set':
                    adjustment = vcAmount - studentobj.virtualCurrencyAmount)
                    studentobj.virtualCurrencyAmount = vcAmount
                elif accumulative_type == 'combine':
                    studentobj.virtualCurrencyAmount += vcAmount

                studentobj.save()
                
                if accumulative_type == 'combine' || (accumulative_type == 'set' and adjustment > 0:
                    ruleCustom = VirtualCurrencyCustomRuleInfo.objects.get(
                        courseID=course, vcRuleID=int(request.POST[studentRuleAttribute]))
                    studentVC = StudentVirtualCurrencyRuleBased()
                    studentVC.courseID = course
                    studentVC.studentID = studentobj.studentID
                    studentVC.vcRuleID = ruleCustom
                    if accumulative_type == 'combine':
                        studentVC.value = vcAmount
                    else:
                        studentVC.value = adjustment
                    studentVC.save()
                    
                    studentAddBadgeLog = BadgesVCLog()
                    studentAddBadgeLog.timestamp = current_localtime()
                    studentAddBadgeLog.courseID = course
                    vc_award_type = "Add" if accumulative_type == 'combine' else "Set"
                    log_data = create_badge_vc_log_json(
                        request.user, studentVC, "VC", "Manual", vc_award_type=vc_award_type)
                    studentAddBadgeLog.log_data = json.dumps(log_data)
                    studentAddBadgeLog.save()
                else:
                    # This is the case which covers negative adjustments
                    # These should show up as spending for things to make sense
                    # Note: ideally this whole bit could be written differently so that
                    # earning and spending aren't two separate types to being with
                    # -Keith
                    svct = StudentVirtualCurrencyTransactions()
                    svct.courseID = course
                    svct.studentID = studentobj.studentID
                    svct.studentEvent = 
                    
                virtual_currency_amount = abs(vcAmount)
                if accumulative_type == 'set':
                    virtual_currency_amount = abs(
                        prev_amount - studentobj.virtualCurrencyAmount)

                if prev_amount > studentobj.virtualCurrencyAmount:
                    notify.send(None, recipient=studentobj.studentID.user, actor=request.user, verb='You lost '+str(virtual_currency_amount)+' course bucks',
                                nf_type='Decrease VirtualCurrency', extra=json.dumps({"course": str(course.courseID), "name": str(course.courseName), "related_link": '/oneUp/students/Transactions'}))
                elif prev_amount < studentobj.virtualCurrencyAmount:
                    register_event(Event.virtualCurrencyEarned, request,
                                   studentobj.studentID, objectId=virtual_currency_amount)
                    notify.send(None, recipient=studentobj.studentID.user, actor=request.user, verb='You earned '+str(virtual_currency_amount)+' course bucks',
                                nf_type='Increase VirtualCurrency', extra=json.dumps({"course": str(course.courseID), "name": str(course.courseName), "related_link": '/oneUp/students/Transactions'}))

            return redirect('AddVirtualCurrency.html')
