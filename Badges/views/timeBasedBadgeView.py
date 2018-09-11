'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

import glob, os

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Instructors.views.utils import initialContextDict
from Badges.models import Badges, BadgesInfo
from django.views.decorators.http import condition
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_variable
@login_required
def timeBasedBadgeView(request):
 
    context_dict,current_course = initialContextDict(request);
        
    extractPaths(context_dict) 
    if request.method == 'GET':
        if 'badgeID' in request.GET:    
        # Getting the Badge information which has been selected
            if request.GET['badgeID']:
                badgeId = request.GET['badgeID']
                badgeInfo = BadgesInfo.objects.get(badgeID=badgeId)
                if not badgeInfo.manual:
                    badge = Badges.objects.get(badgeID=badgeId)
                    context_dict = setUpContextDictForConditions(context_dict,current_course,badge.ruleID)
                else: 
                    context_dict = setUpContextDictForConditions(context_dict,current_course,None)
                    
                # The range part is the index numbers.  
                context_dict['badge'] = badgeInfo 
                context_dict['edit'] = True
                
                print("badgeID")
                
            else:
            ## This is for when a non-existent badgeID gets passed.  It shouldn't normally happen, but could occur due to stale page data.
                context_dict = setUpContextDictForConditions(context_dict,current_course,None)
                print("no badgeID") 
            
        else:
        ##this is the case of creating a new badge
            context_dict = setUpContextDictForConditions(context_dict,current_course,None)
            print("no badgeID") 
                
        if 'manualBadgeID' in request.GET:
            if request.GET['manualBadgeID']:
                badgeId = request.GET['manualBadgeID']
                badge = BadgesInfo.objects.get(badgeID=badgeId)
                    
                context_dict['isManualBadge'] = True
                # The range part is the index numbers.  
                context_dict['badge'] = badge 
                context_dict['edit'] = True
                
                print("badgeID")
            
            
                
        ## check if the conditional box should be displayed or it is a manually assigned badge  
        if 'isManualBadge' in request.GET:
            if request.GET['isManualBadge'] == 'true':
                
                context_dict['isManualBadge'] = True
            else:
                context_dict['isManualBadge'] = False

        context_dict = createTimePeriodContext(context_dict) 
    
        return render(request,'Badges/TimeBasedBadge.html', context_dict)
    elif request.method == 'POST':
        # Create the badge

        # Create periodic task
        ranking = int(request.POST['ranking'])
        timePeriodSelected = int(request.POST['timePeriodSelected'])
        periodicVariableSelected = int(request.POST['periodicVariableSelected'])
        setup_periodic_variable(periodicVariableSelected, current_course, timePeriodSelected, number_of_top_students=ranking, badge_id=1)

def extractPaths(context_dict): #function used to get the names from the file location
    imagePath = []
    
    for name in glob.glob('static/images/badges/*'):
        name = name.replace("\\","/")
        imagePath.append(name)
        print(name)
    
    context_dict["imagePaths"] = zip(range(1,len(imagePath)+1), imagePath)

def createTimePeriodContext(context_dict):

    context_dict['periodicVariables'] = [v for _, v in PeriodicVariables.periodicVariables.items()]
    context_dict['timePeriods'] = [t for _, t in TimePeriods.timePeriods.items()]
    return context_dict