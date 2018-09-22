'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
from django.shortcuts import render

import glob, os

from django.contrib.auth.decorators import login_required
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Instructors.views.utils import initialContextDict, utcDate
from Badges.models import Badges, BadgesInfo, PeriodicBadges
from django.views.decorators.http import condition
from django.shortcuts import redirect
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_variable,\
    delete_periodic_task
from Students.models import Student

@login_required
def timeBasedBadgeView(request):
 
    context_dict,current_course = initialContextDict(request)
        
    extractPaths(context_dict) 
    if request.method == 'GET':
        if 'TimeBasedBadgeID' in request.GET:
            if request.GET['TimeBasedBadgeID']:
                badgeId = request.GET['TimeBasedBadgeID']
                badge = PeriodicBadges.objects.get(badgeID=badgeId, courseID=current_course)
                    
                # The range part is the index numbers.  
                context_dict['badge'] = badge 
                context_dict['edit'] = True            
        else:
            context_dict['edit'] = False 

        context_dict = createTimePeriodContext(context_dict) 
    
        return render(request,'Badges/TimeBasedBadge.html', context_dict)

    if request.method == 'POST':
        selectorMap = {
            "TopN": 0, "All": 1, "Random": 2
        }
        selectors = request.POST.get("selectors")

        if 'delete' in request.POST:
            periodic_badge = PeriodicBadges.objects.get(badgeID=request.POST['badgeId'], courseID=current_course)
            periodic_badge.delete()
            
        elif 'edit' in request.POST:
            # Edit badge
            periodic_badge = PeriodicBadges.objects.get(badgeID=request.POST['badgeId'], courseID=current_course)

            # Delete Periodic Task then recreate it
            delete_periodic_task(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), award_type="badge", course=current_course)
            
            if 'badgeName' in request.POST:
                periodic_badge.badgeName = request.POST['badgeName']
        
            if 'badgeDescription' in request.POST:
                periodic_badge.badgeDescription = request.POST['badgeDescription']   

            periodic_badge.courseID = current_course
            periodic_badge.badgeImage = request.POST['badgeImage']
            periodic_badge.isPeriodic = True
            periodic_badge.periodicType = selectorMap[selectors]
            periodic_badge.periodicVariableID = request.POST['periodicVariableSelected']
            periodic_badge.timePeriodID = request.POST['timePeriodSelected']
            periodic_badge.threshold = request.POST['threshold']
            periodic_badge.operatorType = request.POST['operator']
            periodic_badge.lastModified = utcDate()

            if selectors == "TopN":
                periodic_badge.numberOfAwards = int(request.POST['numberOfAwards'])
                periodic_badge.isRandom = None
            elif selectors == "Random":
                periodic_badge.isRandom = True
                periodic_badge.numberOfAwards = None

            periodic_badge.save()

            # Recreate the Periodic Task based on the type
            if selectors == "TopN":
                setup_periodic_variable(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, time_period=int(periodic_badge.timePeriodID), number_of_top_students=int(periodic_badge.numberOfAwards), threshold=int(periodic_badge.threshold), operator_type=periodic_badge.operatorType, badge_id=int(periodic_badge.badgeID))
            elif selectors == "Random":
                setup_periodic_variable(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, time_period=int(periodic_badge.timePeriodID), threshold=int(periodic_badge.threshold), operator_type=periodic_badge.operatorType, is_random=periodic_badge.isRandom, badge_id=int(periodic_badge.badgeID))
            else:
                setup_periodic_variable(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, time_period=int(periodic_badge.timePeriodID), threshold=int(periodic_badge.threshold), operator_type=periodic_badge.operatorType, badge_id=int(periodic_badge.badgeID))
        else:
            # Create the badge
            periodic_badge = PeriodicBadges()
            
            if 'badgeName' in request.POST:
                periodic_badge.badgeName = request.POST['badgeName']
        
            if 'badgeDescription' in request.POST:
                periodic_badge.badgeDescription = request.POST['badgeDescription']   

            periodic_badge.courseID = current_course
            periodic_badge.badgeImage = request.POST['badgeImage']
            periodic_badge.isPeriodic = True
            periodic_badge.periodicType = selectorMap[selectors]
            periodic_badge.periodicVariableID = request.POST['periodicVariableSelected']
            periodic_badge.timePeriodID = request.POST['timePeriodSelected']
            periodic_badge.threshold = request.POST['threshold']
            periodic_badge.operatorType = request.POST['operator']
                
            if selectors == "TopN":
                periodic_badge.numberOfAwards = int(request.POST['numberOfAwards'])
                periodic_badge.isRandom = None
            elif selectors == "Random":
                periodic_badge.isRandom = True
                periodic_badge.numberOfAwards = None

            periodic_badge.save()

            # Create the Periodic Task based on the type
            if selectors == "TopN":
                setup_periodic_variable(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, time_period=int(periodic_badge.timePeriodID), number_of_top_students=int(periodic_badge.numberOfAwards), threshold=int(periodic_badge.threshold), operator_type=periodic_badge.operatorType, badge_id=int(periodic_badge.badgeID))
            elif selectors == "Random":
                setup_periodic_variable(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, time_period=int(periodic_badge.timePeriodID), threshold=int(periodic_badge.threshold), operator_type=periodic_badge.operatorType, is_random=periodic_badge.isRandom, badge_id=int(periodic_badge.badgeID))
            else:
                setup_periodic_variable(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, time_period=int(periodic_badge.timePeriodID), threshold=int(periodic_badge.threshold), operator_type=periodic_badge.operatorType, badge_id=int(periodic_badge.badgeID))
        
        return redirect('PeriodicBadges.html')
        

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