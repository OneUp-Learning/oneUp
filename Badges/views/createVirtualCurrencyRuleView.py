'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Courses, Activities
from Badges.enums import SystemVariable, dict_dict_to_zipped_list,\
    displayCircumstance


# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def CreateVcRule(request):
    
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
    
    sysIndex = []
    sysDisplayName = []
    systemVariableObjects= dict_dict_to_zipped_list(SystemVariable.systemVariables,['index','displayName', 'displayCircumstances'])  
    # Select only the system variables that are for virtual currency
    for i, sysVars, display in systemVariableObjects:
        for key, v in display.items():
            if key == displayCircumstance.virtualCurrency:
                sysIndex.append(i)
                sysDisplayName.append(sysVars)
        
    challengeObjects=[] 
    activityObjects=[]    
    chall=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse)
    for challID in chall:
        unassignID = challID.challengeID   

    challenges = Challenges.objects.filter(courseID=currentCourse)
    activities = Activities.objects.filter(courseID=currentCourse)       
    for challenge in challenges:
        # This code will actually append the challenges that are unassigned (except for the last one
        # that we found in the above for loop) along with all other assigned challenges
        if challenge.challengeID != unassignID:    
            challengeObjects.append(challenge)
            print("challenge: "+str(challenge))
    for activity in activities:
        activityObjects.append(activity)  
        print("activity: "+str(activity))        
    # The range part is the index numbers.
    context_dict['systemVariables'] = zip(range(1, len(sysIndex)+1), sysIndex, sysDisplayName)
    context_dict['challenges'] = zip(range(1,challenges.count()+1),challengeObjects)
    context_dict['activities'] = zip(range(1,activities.count()+1),activityObjects)

    return render(request,'Badges/CreateVirtualCurrencyRule.html', context_dict)

