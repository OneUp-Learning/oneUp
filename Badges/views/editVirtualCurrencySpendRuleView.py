'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments
from Instructors.models import Challenges,Courses
from Instructors.views.utils import initialContextDict
from Badges.enums import dict_dict_to_zipped_list, Event

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import get_mandatory_conditions_without_or_and_not, filter_out_associated_challenges, leaf_condition_to_tuple,\
    get_associated_challenge_if_exists
from setuptools.command.build_ext import if_dl

@login_required
def EditVirtualCurrencySpendRule(request):
 
    context_dict, currentCourse = initialContextDict(request)
            
    # Getting all the Spending Rules information which has been selected
    rules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, courseID = currentCourse)
    eventIndex = []
    eventName = []
    eventDescription = []
    eventEnabled = []
    eventAmount = []
    eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description'])  
    
    # Select only the system variables that are for virtual currency
    for i, eName, eDescription in eventObjects:
        if i >= 850:
            found = False
            for rule in rules:
                if rule.vcRuleName == eName:
                    eventIndex.append(i)
                    eventName.append(eName)
                    eventDescription.append(eDescription)
                    if ActionArguments.objects.filter(ruleID=rule.ruleID).exists():
                        amount = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
                    else:
                        amount = 0
                    eventAmount.append(amount)
                    eventEnabled.append(True)
                    found = True
                    break   
            if not found:
                eventIndex.append(i)
                eventName.append(eName)
                eventDescription.append(eDescription)
                eventEnabled.append(False)
                eventAmount.append(0) 
                    
    context_dict['events'] = zip(range(1, len(eventIndex)+1), eventIndex, eventName, eventDescription, eventAmount, eventEnabled)
    
    return render(request,'Badges/EditVirtualCurrencySpendRule.html', context_dict)