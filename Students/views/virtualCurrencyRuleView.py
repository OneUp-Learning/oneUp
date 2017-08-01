'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, Courses, ActionArguments, Rules
from Badges.enums import Action
from Students.models import Student, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def VirtualCurrencyDisplay(request):

    context_dict,currentCourse = studentInitialContextDict(request)
 
#     context_dict = { }
#     
#     context_dict["logged_in"]=request.user.is_authenticated()
#     if request.user.is_authenticated():
#         context_dict["username"]=request.user.username
#         sID = Student.objects.get(user=request.user)
#     
#     # check if course was selected
#     if 'currentCourseID' in request.session:
#         currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
#         context_dict['course_Name'] = currentCourse.courseName
#         student = Student.objects.get(user=request.user)   
#         st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
#         context_dict['avatar'] = st_crs.avatarImage          
#         
#     else:
#         context_dict['course_Name'] = 'Not Selected'
        
    vcEarningRuleID = [] 
    vcEarningRuleName = []
    vcEarningRuleDescription = []
    vcEarningRuleAmount = []
    vcSpendingRuleID = [] 
    vcSpendingRuleName = []
    vcSpendingRuleDescription = []
    vcSpendingRuleAmount = []
    countEarningRules = 0
    countSpendingRules = 0
            
    #Displaying the list of rules from database
    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse)
    for rule in vcRules:
        if rule.ruleID.actionID == Action.increaseVirtualCurrency:
            vcEarningRuleID.append(rule.vcRuleID)
            vcEarningRuleName.append(rule.vcRuleName)
            vcEarningRuleDescription.append(rule.vcRuleDescription)
            value = -9000000000
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                value = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
            vcEarningRuleAmount.append(value)
            countEarningRules = countEarningRules+1        
        else:
            vcSpendingRuleID.append(rule.vcRuleID)
            vcSpendingRuleName.append(rule.vcRuleName)
            vcSpendingRuleDescription.append(rule.vcRuleDescription)
            value = -9000000000
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                value = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
            vcSpendingRuleAmount.append(value)
            countSpendingRules = countSpendingRules+1
             
        # The range part is the index numbers.
    context_dict['vcEarningRuleInfo'] = zip(range(1,countEarningRules+1),vcEarningRuleID,vcEarningRuleName, vcEarningRuleDescription, vcEarningRuleAmount)
    context_dict['vcSpendingRuleInfo'] = zip(range(1,countSpendingRules+1),vcSpendingRuleID,vcSpendingRuleName, vcSpendingRuleDescription, vcSpendingRuleAmount)

    return render(request,'Students/VirtualCurrencyRules.html', context_dict)