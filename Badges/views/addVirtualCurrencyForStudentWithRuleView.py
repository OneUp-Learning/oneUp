from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Students.models import StudentRegisteredCourses, Student, StudentVirtualCurrencyRuleBased
from Badges.systemVariables import logger
from notify.signals import notify  
import json


@login_required
def addVirtualCurrencyForStudentWithRuleView(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        if request.method == 'GET':
            students = StudentRegisteredCourses.objects.filter(courseID = course).order_by("studentID__user__last_name")
            studentID = []
            studentName= []
            studentCurrencyVC = []
            for studentobj in students:
                studentID.append(studentobj.studentID)
                if studentobj.studentID.isTestStudent:
                    studentName.append(studentobj.studentID.user.get_full_name() + " (Test Student)")
                else:
                    studentName.append(studentobj.studentID.user.get_full_name())
                studentCurrencyVC.append(studentobj.virtualCurrencyAmount)
            
            rules = VirtualCurrencyCustomRuleInfo.objects.filter(courseID = course)
            customRules = [r for r in rules if not hasattr(r, 'virtualcurrencyruleinfo')]
            
            allRulesID = []
            allRulesName = []
            for rule in customRules:
                allRulesID.append(rule.vcRuleID)
                allRulesName.append(rule.vcRuleName)
            
            
            context_dict['students'] = (zip(studentID, studentName, studentCurrencyVC))#, key=lambda tup: tup[1])
                                              
            context_dict['rules'] = list(zip(allRulesID, allRulesName))
            return render(request, 'Badges/AddVirtualCurrency.html', context_dict)
        elif request.method == 'POST':
            logger.debug(request.POST)
            students = StudentRegisteredCourses.objects.filter(courseID = course)
            
            for studentobj in students:
                studentValAttribute = str(studentobj.studentID) + '_Value'
                studentRuleAttribute = str(studentobj.studentID) + '_Rule'
                accumulative_type = request.POST.get(str(studentobj.studentID) + '_type')
                
                if request.POST[studentValAttribute] == '' or request.POST[studentRuleAttribute] == '':
                    continue
                
                # Virtual currency should be positive
                vcAmount = int(request.POST[studentValAttribute])
                if vcAmount < 0:
                    vcAmount = 0
                prev_amount = studentobj.virtualCurrencyAmount
                if accumulative_type == 'set':
                    studentobj.virtualCurrencyAmount = vcAmount
                elif accumulative_type == 'combine':
                    studentobj.virtualCurrencyAmount += vcAmount
                
                studentobj.save()
                
                ruleCustom = VirtualCurrencyCustomRuleInfo.objects.get(courseID = course, vcRuleID = int(request.POST[studentRuleAttribute]))
                studentVC = StudentVirtualCurrencyRuleBased()
                studentVC.courseID = course
                studentVC.studentID = studentobj.studentID
                studentVC.vcRuleID = ruleCustom
                
                if accumulative_type == 'set':
                    studentVC.value = vcAmount - prev_amount
                else:
                    studentVC.value = vcAmount
                studentVC.save()

                virtual_currency_amount = abs(vcAmount)
                if accumulative_type == 'set':
                    virtual_currency_amount = abs(prev_amount - studentobj.virtualCurrencyAmount)

                if prev_amount > studentobj.virtualCurrencyAmount:
                    notify.send(None, recipient=studentobj.studentID.user, actor=request.user, verb='You lost '+str(virtual_currency_amount)+' course bucks', nf_type='Decrease VirtualCurrency', extra=json.dumps({"course": str(course.courseID)}))
                elif prev_amount < studentobj.virtualCurrencyAmount:
                    notify.send(None, recipient=studentobj.studentID.user, actor=request.user, verb='You earned '+str(virtual_currency_amount)+' course bucks', nf_type='Increase VirtualCurrency', extra=json.dumps({"course": str(course.courseID)}))
                
            
            return redirect('AddVirtualCurrency.html')
            