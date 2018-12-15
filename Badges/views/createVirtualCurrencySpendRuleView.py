from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.views.utils import initialContextDict
from Badges.conditions_util import setUpContextDictForConditions
from Badges.systemVariables import logger

from Badges.models import VirtualCurrencyCustomRuleInfo, ActionArguments

# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def create_vc_spend_rule(request):
    
    context_dict,currentCourse = initialContextDict(request)
    if request.method == 'GET':
        if 'vcRuleID' in request.GET:
            rule = VirtualCurrencyCustomRuleInfo.objects.get(vcRuleID=request.GET['vcRuleID'], courseID= currentCourse)
            context_dict['ruleName'] = rule.vcRuleName
            context_dict['ruleDescription'] = rule.vcRuleDescription
            context_dict['ruleAmount'] = rule.vcRuleAmount or 0
            context_dict['ruleLimit'] = rule.vcRuleLimit
            context_dict['vcRuleID'] = request.GET['vcRuleID']

    return render(request,'Badges/CreateVirtualCurrencySpendRule.html', context_dict)