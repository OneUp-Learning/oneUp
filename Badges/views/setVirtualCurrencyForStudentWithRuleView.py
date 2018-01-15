from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Students.models import StudentRegisteredCourses, Student
from Badges.systemVariables import logger


@login_required
def setVirtualCurrencyForStudentWithRuleView(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        if request.method == 'GET':
            students = StudentRegisteredCourses.objects.filter(courseID = course)
            studentID = []
            studentName= []
            for studentobj in students:
                studentID.append(studentobj.studentID)
                studentName.append(studentobj.studentID.user.get_full_name())
            
            rules = VirtualCurrencyRuleInfo.objects.filter(courseID = course)
            customRules = VirtualCurrencyCustomRuleInfo.objects.filter(courseID = course)
            
            allRulesID = []
            allRulesName = []
            for rule in rules:
                allRulesID.append(rule.vcRuleID)
                allRulesName.append(rule.vcRuleName)
            for rule in customRules:
                allRulesID.append(rule.vcRuleID)
                allRulesName.append(rule.vcRuleName)
            
            
            context_dict['students'] = list(zip(studentID, studentName))
            context_dict['rules'] = list(zip(allRulesID, allRulesName))
            return render(request, 'Badges/SettingVirtualCurrency.html', context_dict)
        elif request.method == 'POST':
            logger.debug(request.POST)
            students = StudentRegisteredCourses.objects.filter(courseID = course)
            selectedStudents = []
            for studentobj in students:
                studentValAttribute = str(studentobj.studentID) + '_Value'
                studentRuleAttribute = str(studentobj.studentID) + '_Rule'
                
                if request.POST[studentValAttribute] == '' or request.POST[studentRuleAttribute] == '':
                    continue
                
                logger.debug(studentobj.studentID)
            
            return redirect('SettingVirtualCurrency.html')
            