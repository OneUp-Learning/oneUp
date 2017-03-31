'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.template import RequestContext
from django.shortcuts import render

from Badges.models import Courses, VirtualCurrencyRuleInfo, ActionArguments
from Badges.enums import  Event 
from django.contrib.auth.decorators import login_required

@login_required
def VirtualCurrencyList(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    vcRuleID = [] 
    vcRuleName = []
    vcAmount = []
    
    vcsRuleID = [] 
    vcsRuleName = []
    vcsAmount = [] 
        #Displaying the list of challenges from database
    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse)
    for rule in vcRules:
        if rule.vcRuleType == True:
            vcRuleID.append(rule.vcRuleID)
            vcRuleName.append(rule.vcRuleName)
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                vcAmount.append(ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue)
            else:
                vcAmount.append(0)
        else:
            vcsRuleID.append(rule.vcRuleID)
            vcsRuleName.append(rule.vcRuleName)
            if (ActionArguments.objects.filter(ruleID=rule.ruleID).exists()):
                vcsAmount.append(ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue)
            else:
                vcsAmount.append(0)
                    
        # The range part is the index numbers.
    context_dict['vcRuleInfo'] = zip(range(1,len(vcRuleID)+1),vcRuleID,vcRuleName,vcAmount)
    context_dict['vcsRuleInfo'] = zip(range(1,len(vcsRuleID)+1),vcsRuleID,vcsRuleName,vcsAmount)

    #return render(request,'Badges/ListBadges.html', context_dict)
    return render(request,'Badges/InstructorVirtualCurrencyList.html', context_dict)