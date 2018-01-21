from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Students.models import StudentRegisteredCourses, Student, StudentVirtualCurrency
from Badges.systemVariables import logger


@login_required
def addVirtualCurrencyForStudentWithRuleView(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        if request.method == 'GET':
            students = StudentRegisteredCourses.objects.filter(courseID = course)
            studentID = []
            studentName= []
            studentCurrencyVC = []
            for studentobj in students:
                studentID.append(studentobj.studentID)
                studentName.append(studentobj.studentID.user.get_full_name())
                studentCurrencyVC.append(studentobj.virtualCurrencyAmount)
            
            rules = VirtualCurrencyCustomRuleInfo.objects.filter(courseID = course)
            customRules = [r for r in rules if not hasattr(r, 'virtualcurrencyruleinfo')]
            
            allRulesID = []
            allRulesName = []
            for rule in customRules:
                allRulesID.append(rule.vcRuleID)
                allRulesName.append(rule.vcRuleName)
            
            
            context_dict['students'] = list(zip(studentID, studentName, studentCurrencyVC))
            context_dict['rules'] = list(zip(allRulesID, allRulesName))
            return render(request, 'Badges/AddVirtualCurrency.html', context_dict)
        elif request.method == 'POST':
            logger.debug(request.POST)
            students = StudentRegisteredCourses.objects.filter(courseID = course)
            for studentobj in students:
                studentValAttribute = str(studentobj.studentID) + '_Value'
                studentRuleAttribute = str(studentobj.studentID) + '_Rule'
                
                if request.POST[studentValAttribute] == '' or request.POST[studentRuleAttribute] == '':
                    continue
                
                # Virtual currency should be positive
                vcAmount = int(request.POST[studentValAttribute])
                if vcAmount < 0:
                    vcAmount = 0
                    
                studentobj.virtualCurrencyAmount += vcAmount
                studentobj.save()
                
                ruleCustom = VirtualCurrencyCustomRuleInfo.objects.get(courseID = course, vcRuleID = int(request.POST[studentRuleAttribute]))
                studentVC = StudentVirtualCurrency()
                studentVC.studentID = studentobj.studentID
                studentVC.vcRuleID = ruleCustom
                studentVC.value = vcAmount
                studentVC.save()
                logger.debug(studentobj.studentID)
            
            return redirect('AddVirtualCurrency.html')
            