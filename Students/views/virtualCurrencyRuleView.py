'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, Courses, ActionArguments
from Students.models import Student, StudentRegisteredCourses

from django.contrib.auth.decorators import login_required

@login_required
def VirtualCurrencyDisplay(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        student = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage          
        
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    vcRuleID = [] 
    vcRuleName = []
    vcRuleDescription = []
    vcRuleAmount = []
        
    #Displaying the list of rules from database
    vcRules = VirtualCurrencyRuleInfo.objects.filter(courseID=currentCourse)
    for rule in vcRules:
        vcRuleID.append(rule.vcRuleID)
        vcRuleName.append(rule.vcRuleName)
        vcRuleDescription.append(rule.vcRuleDescription)
        vcRuleAmount.append(ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue)
                    
        # The range part is the index numbers.
    context_dict['vcRuleInfo'] = zip(range(1,vcRules.count()+1),vcRuleID,vcRuleName, vcRuleDescription, vcRuleAmount)

    #return render(request,'Badges/ListBadges.html', context_dict)
    return render(request,'Students/VirtualCurrencyRules.html', context_dict)