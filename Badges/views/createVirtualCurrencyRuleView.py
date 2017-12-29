'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.views.utils import initialContextDict
from Badges.conditions_util import setUpContextDictForConditions


# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def CreateVcRule(request):
    
    context_dict,currentCourse = initialContextDict(request);

    context_dict = setUpContextDictForConditions(context_dict,currentCourse)
    
    context_dict['initialCond'] = "'empty'"

    context_dict['editOrCreate']="create"
    context_dict['capitalEditOrCreate']="Create"
    context_dict['saveOrCreate']="create"
    context_dict['captialSaveOrCreate'] = "Create"

    return render(request,'Badges/EditVirtualCurrencyRule.html', context_dict)

