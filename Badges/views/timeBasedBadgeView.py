'''
Created on Nov 3, 2014
Last modified 09/02/2016

'''
import glob
import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import condition

from Badges.conditions_util import (databaseConditionToJSONString,
                                    setUpContextDictForConditions)
from Badges.models import Badges, BadgesInfo, PeriodicBadges
from Badges.periodicVariables import (PeriodicVariables, TimePeriods,
                                      delete_periodic_task,
                                      setup_periodic_badge)
from Instructors.views.utils import current_localtime, initialContextDict
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
                context_dict['is_value'] = not badge.threshold in ['avg', 'max']
                if determineIfStreakAward(badge.periodicVariableID):
                    context_dict['checkbox'] = badge.resetStreak         
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
            if PeriodicBadges.objects.filter(badgeID=request.POST['badgeId'], courseID=current_course).exists():
                periodic_badge = PeriodicBadges.objects.filter(badgeID=request.POST['badgeId'], courseID=current_course)[0]
                periodic_badge.delete()
        else:
            if 'badgeId' in request.POST:
                periodic_badge = PeriodicBadges.objects.get(badgeID=request.POST['badgeId'], courseID=current_course)
            else:
                periodic_badge = PeriodicBadges()
            
            if 'edit' in request.POST:
                periodic_badge = PeriodicBadges.objects.get(badgeID=request.POST['badgeId'], courseID=current_course)

            if 'badgeName' in request.POST:
                periodic_badge.badgeName = request.POST['badgeName']
        
            if 'badgeDescription' in request.POST:
                periodic_badge.badgeDescription = request.POST['badgeDescription']   
                
            if 'resetStreak' in request.POST:
                if int(request.POST['resetStreak']):
                    periodic_badge.resetStreak = True
                else:
                    periodic_badge.resetStreak = False

            periodic_badge.courseID = current_course
            periodic_badge.badgeImage = request.POST['badgeImage']
            periodic_badge.isPeriodic = True
            periodic_badge.periodicVariableID = request.POST['periodicVariableSelected']
            periodic_badge.timePeriodID = request.POST['timePeriodSelected']
            periodic_badge.threshold = request.POST['threshold']
            periodic_badge.operatorType = request.POST['operator']
            periodic_badge.lastModified = current_localtime()

            streakObject = determineIfStreakAward(int(request.POST['periodicVariableSelected']))
    
            if 'selectors' in request.POST:
                periodic_badge.periodicType = selectorMap[selectors]
    
                if selectors == "TopN":
                    if not streakObject: 
                        periodic_badge.numberOfAwards = int(request.POST['numberOfAwards'])
                        periodic_badge.isRandom = None
                elif selectors == "Random":
                    periodic_badge.isRandom = True
                    periodic_badge.numberOfAwards = None
    
            periodic_badge.save()

            # Delete Periodic Task then recreate it
            if periodic_badge.periodicTask:
                periodic_badge.periodicTask.delete()
            # delete_periodic_task(unique_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), award_type="badge", course=current_course)

            # Recreate the Periodic Task based on the type
            if selectors == "TopN":
                periodic_badge.periodicTask = setup_periodic_badge(request=request, unique_id=int(periodic_badge.badgeID), badge_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, period_index=int(periodic_badge.timePeriodID), number_of_top_students=int(periodic_badge.numberOfAwards), threshold=periodic_badge.threshold, operator_type=periodic_badge.operatorType)
            elif selectors == "Random":
                periodic_badge.periodicTask = setup_periodic_badge(request=request, unique_id=int(periodic_badge.badgeID), badge_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, period_index=int(periodic_badge.timePeriodID), threshold=periodic_badge.threshold, operator_type=periodic_badge.operatorType, is_random=periodic_badge.isRandom)
            else:
                periodic_badge.periodicTask = setup_periodic_badge(request=request, unique_id=int(periodic_badge.badgeID), badge_id=int(periodic_badge.badgeID), variable_index=int(periodic_badge.periodicVariableID), course=current_course, period_index=int(periodic_badge.timePeriodID), threshold=periodic_badge.threshold, operator_type=periodic_badge.operatorType)
            
            periodic_badge.save()
    
        return redirect('PeriodicBadges.html')
        

def extractPaths(context_dict): #function used to get the names from the file location
    imagePath = []
    
    for name in glob.glob('static/images/badges/*'):
        name = name.replace("\\","/")
        imagePath.append(name)
        print(name)
    
    context_dict["imagePaths"] = zip(range(1,len(imagePath)+1), imagePath)

def createTimePeriodContext(context_dict):
    import collections
   
    context_dict['periodicVariables'] = [v for _, v in  sorted(PeriodicVariables.periodicVariables.items())]
    context_dict['timePeriods'] = [t for _, t in TimePeriods.timePeriods.items()]
    return context_dict
def determineIfStreakAward(variableID):
    if  variableID == 1408 or  variableID == 1407 or variableID == 1409 or variableID == 1410:
        return True
    else:
        return False
