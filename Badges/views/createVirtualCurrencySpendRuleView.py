'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render
import glob, os
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Courses
from Badges.enums import dict_dict_to_zipped_list,Event
from Badges.systemVariables import SystemVariable

# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def CreateVcSpendRule(request):
    
    context_dict = { }
        
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    #else:
        #context_dict['course_Name'] = 'Not Selected'
    
    eventIndex = []
    eventName = []
    eventDescription = []
    eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description'])  
    # Select only the system variables that are for virtual currency
    for i, eName, eDescription in eventObjects:
        if i >= 850:
            eventIndex.append(i)
            eventName.append(eName)
            eventDescription.append(eDescription)
                
    # The range part is the index numbers.
    context_dict['events'] = zip(range(1, len(eventIndex)+1), eventIndex, eventName, eventDescription)

    return render(request,'Badges/CreateVirtualCurrencySpendRule.html', context_dict)

