'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments, RuleEvents
from Instructors.views.utils import initialContextDict
from Badges.enums import dict_dict_to_zipped_list, Event

from django.contrib.auth.decorators import login_required

@login_required
def SelectVirtualCurrencySpendRule(request):
 
    context_dict, currentCourse = initialContextDict(request)
            
    # Getting all the Spending Rules information which has been selected
    rules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, courseID = currentCourse)
    eventIndex = []
    eventName = []
    eventDescription = []
    eventEnabled = []
    eventAmount = []
    ruleLimit = []
    eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description'])  
    
    # Select only the system variables that are for virtual currency
    for i, eName, eDescription in eventObjects:
        # removed adjustment event(861) for now since teacher can adjust a student challenge grade and we don’t have a way to restrict number of purchases in course shop :( 
        if i >= 850 and i != 861:
            found = False
            for rule in rules:
                ruleEvent = RuleEvents.objects.get(rule = rule.ruleID)
                if ruleEvent.event == i:
                    eventIndex.append(i)
                    eventName.append(rule.vcRuleName)
                    eventDescription.append(rule.vcRuleDescription)
                    if ActionArguments.objects.filter(ruleID=rule.ruleID).exists():
                        amount = ActionArguments.objects.get(ruleID=rule.ruleID).argumentValue
                    else:
                        amount = 0
                    
                    eventAmount.append(amount)
                    ruleLimit.append(rule.vcRuleLimit)
                    eventEnabled.append(True)
                    found = True
                    break   
            if not found:
                eventIndex.append(i)
                eventName.append(eName)
                eventDescription.append(eDescription)
                eventEnabled.append(False)
                eventAmount.append(0) 
                ruleLimit.append(0)
                    
    context_dict['events'] = zip(range(1, len(eventIndex)+1), eventIndex, eventName, eventDescription, eventAmount, ruleLimit, eventEnabled)
    
    return render(request,'Badges/SelectVirtualCurrencySpendRule.html', context_dict)