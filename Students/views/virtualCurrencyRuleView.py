'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, Courses
from Students.models import Student

from django.contrib.auth.decorators import login_required

@login_required
def VirtualCurrencyDisplay(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)
        context_dict['avatar'] = sID.avatarImage          
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    vcRuleID = [] 
    vcRuleName = []
    vcRuleDescription = []
    vcRuleAmount = []
        
        #Displaying the list of challenges from database
    vcRules = VirtualCurrencyRuleInfo.objects.all()
    for rule in vcRules:
        vcRuleID.append(rule.vcRuleID)
        vcRuleName.append(rule.vcRuleName)
        vcRuleDescription.append(rule.vcRuleDescription)
        vcRuleAmount.append(rule.vcAmount)
                    
        # The range part is the index numbers.
    context_dict['vcRuleInfo'] = zip(range(1,vcRules.count()+1),vcRuleID,vcRuleName, vcRuleDescription, vcRuleAmount)

    #return render(request,'Badges/ListBadges.html', context_dict)
    return render(request,'Students/VirtualCurrencyRules.html', context_dict)