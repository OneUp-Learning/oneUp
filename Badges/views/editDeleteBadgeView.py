'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

import glob, os

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Instructors.views.utils import initialContextDict
from Badges.models import Badges

@login_required
def EditDeleteBadge(request):
 
    context_dict,current_course = initialContextDict(request);
    
    context_dict = setUpContextDictForConditions(context_dict,current_course)
    
    conditions = []
    
    extractPaths(context_dict)
    
    if request.GET:
    
        # Getting the Badge information which has been selected
        if request.GET['badgeID']:
            badgeId = request.GET['badgeID']
            badge = Badges.objects.get(badgeID=badgeId)
            condition = badge.ruleID.conditionID
            
            context_dict['initialCond'] = databaseConditionToJSONString(condition)     
            
                
            # The range part is the index numbers.  
            context_dict['badge'] = badge
            context_dict['conditions'] = zip(range(1,len(conditions)+1),conditions)
            context_dict['edit'] = True
        else:
            context_dict['initialCond'] = "'empty'"

    
    return render(request,'Badges/EditDeleteBadge.html', context_dict)

def extractPaths(context_dict): #function used to get the names from the file location
    imagePath = []
    
    for name in glob.glob('static/images/badges/*'):
        name = name.replace("\\","/")
        imagePath.append(name)
        print(name)
    
    context_dict["imagePaths"] = zip(range(1,len(imagePath)+1), imagePath)