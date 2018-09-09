'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

import glob, os

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Instructors.views.utils import initialContextDict
from Badges.models import Badges, BadgesInfo, PeriodicBadges
from django.views.decorators.http import condition
from django.shortcuts import redirect
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_variable,\
    delete_periodic_task
from Students.models import Student
@login_required
def timeBasedBadgeView(request):
 
    context_dict,current_course = initialContextDict(request);
        
    extractPaths(context_dict) 
    if request.method == 'GET':
        if 'badgeID' in request.GET:    
        # Getting the Badge information which has been selected
            if request.GET['badgeID']:
                badgeId = request.GET['badgeID']
                badgeInfo = PeriodicBadges.objects.get(badgeID=badgeId)
                if not badgeInfo.manual:
                    badge = Badges.objects.get(badgeID=badgeId)
                    context_dict = setUpContextDictForConditions(context_dict,current_course,badge.ruleID)
                else: 
                    context_dict = setUpContextDictForConditions(context_dict,current_course,None)
                    
                # The range part is the index numbers.  
                context_dict['badge'] = badgeInfo 
                
                print("badgeID")
                
            else:
            ## This is for when a non-existent badgeID gets passed.  It shouldn't normally happen, but could occur due to stale page data.
                context_dict = setUpContextDictForConditions(context_dict,current_course,None)
                print("no badgeID") 
            
        else:
        ##this is the case of creating a new badge
            context_dict = setUpContextDictForConditions(context_dict,current_course,None)
            print("no badgeID") 
                
        if 'TimeBasedBadgeID' in request.GET:
            if request.GET['TimeBasedBadgeID']:
                badgeId = request.GET['TimeBasedBadgeID']
                badge = PeriodicBadges.objects.get(badgeID=badgeId)
                    
                context_dict['TimeBasedBadgeID'] = request.GET['TimeBasedBadgeID']
                # The range part is the index numbers.  
                context_dict['badge'] = badge 
                context_dict['edit'] = True
                
                print("badgeID")
            
            
                
        ## check if the conditional box should be displayed or it is a manually assigned badge  
        if 'isTimeBasedBadge' in request.GET:
            if request.GET['isTimeBasedBadge'] == 'true':
                
                context_dict['isTimeBasedBadge'] = True
            else:
                context_dict['isTimeBasedBadge'] = False

        context_dict = createTimePeriodContext(context_dict) 
    
        return render(request,'Badges/TimeBasedBadge.html', context_dict)
    elif request.method == 'POST':
         
        if 'delete' in request.POST:
            delete_periodic_task(request.POST['periodicVariableSelected'], current_course, request.POST['timePeriodSelected'], number_of_top_students=request.POST['ranking'], badge_id=request.POST['badgeId'])
            PeriodicBadges.objects.get(badgeID=request.POST['badgeId']).delete()
            return redirect('Badges.html')
        if 'edit' in request.POST:
            # Edit badge
            delete_periodic_task(request.POST['periodicVariableSelected'], current_course, request.POST['timePeriodSelected'], number_of_top_students=request.POST['ranking'], badge_id=request.POST['badgeId'])
            studentPeriodicBadge = PeriodicBadges.objects.get(badgeID=request.POST['badgeId'])
        else:
            # Create the badge
            studentPeriodicBadge = PeriodicBadges()
            
        if 'ranking' in request.POST:
            studentPeriodicBadge.numberOfAwards = request.POST['ranking']
        
        if 'badgeImage' in request.POST:
            studentPeriodicBadge.badgeImage = request.POST['badgeImage']
            
        if 'badgeName' in request.POST:
            studentPeriodicBadge.badgeName = request.POST['badgeName']
        
        if 'badgeDescription' in request.POST:
            studentPeriodicBadge.badgeDescription = request.POST['badgeDescription']   
            
        if 'timePeriodSelected' in request.POST:
            studentPeriodicBadge.timePeriodID = request.POST['timePeriodSelected']
            
        if 'periodicVariableSelected' in request.POST:
            studentPeriodicBadge.periodicVariableID = request.POST['periodicVariableSelected']
            
            
            studentPeriodicBadge.courseID = current_course
            studentPeriodicBadge.isPeriodic = True
            studentPeriodicBadge.save()

        # Create periodic task
        ranking = int(request.POST['ranking'])
        timePeriodSelected = int(request.POST['timePeriodSelected'])
        periodicVariableSelected = int(request.POST['periodicVariableSelected'])
        
        setup_periodic_variable(studentPeriodicBadge.badgeID, periodicVariableSelected, current_course, timePeriodSelected, number_of_top_students=ranking, badge_id=studentPeriodicBadge.badgeID)
        return redirect('Badges.html')
        
        

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