'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments
from Instructors.models import Challenges,Courses
from Badges.enums import dict_dict_to_zipped_list, Event

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import get_mandatory_conditions_without_or_and_not, filter_out_associated_challenges, leaf_condition_to_tuple,\
    get_associated_challenge_if_exists
from setuptools.command.build_ext import if_dl

    
def EditVirtualCurrencySpendRule(request):
 
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
            
    # Getting the Rule information which has been selected
    rules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False)
        
    eventIndex = []
    eventName = []
    eventDescription = []
    eventEnabled = []
    eventAmount = []
    eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description'])  
    # Select only the system variables that are for virtual currency
    for i, eName, eDescription in eventObjects:
        found = False
        for rule in rules:
            if i >= 850:
                if rule.vcRuleName == eName:
                    eventIndex.append(i)
                    eventName.append(eName)
                    eventDescription.append(eDescription)
                    eventAmount.append((ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue))
                    eventEnabled.append(True)
                    found = True
                    break
        if found == False:
            eventIndex.append(i)
            eventName.append(eName)
            eventDescription.append(eDescription)
            eventEnabled.append(False)
            eventAmount.append(0) 
                    
    print(eventName) 
    # The range part is the index numbers.
    context_dict['events'] = zip(range(1, len(eventIndex)+1), eventIndex, eventName, eventDescription, eventAmount, eventEnabled)
    
    return render(request,'Badges/EditVirtualCurrencySpendRule.html', context_dict)