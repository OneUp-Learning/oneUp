'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.views.utils import initialContextDict
from Badges.conditions_util import setUpContextDictForConditions
from Badges.systemVariables import logger

from Badges.enums import AwardFrequency, ApplauseOption

# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def CreateVARule(request):
    
    context_dict,currentCourse = initialContextDict(request)

    context_dict = setUpContextDictForConditions(context_dict,currentCourse, None)
    
    context_dict['editOrCreate']="create"
    context_dict['capitalEditOrCreate']="Create"
    context_dict['saveOrCreate']="create"
    context_dict['captialSaveOrCreate'] = "Create"
    context_dict['isRuleCustom'] = request.GET['isRuleCustom'] in ['true', 'True']
    
    applausArr = []    
    for x in ApplauseOption.applauseOption :         
        applausArr.append( ApplauseOption.applauseOption.setdefault(x))
     
    context_dict['applauseOptionStruct'] = applausArr
    
    return render(request,'Badges/EditVirtualApplauseRule.html', context_dict)

