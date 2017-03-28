'''
Created on Nov 3, 2014
Last modified: 09/02/2016

'''
from django.template import RequestContext
from django.shortcuts import render
import glob, os
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Courses
from Badges.enums import SystemVariable, dict_dict_to_zipped_list


# This sets up the page used to create the badge, but does not, in fact, create any badges.
# Badges are actually created in the saveBadgeView class.

@login_required
def CreateBadge(request):
    
    context_dict = { }
    
    extractPaths(context_dict)
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    #else:
        #context_dict['course_Name'] = 'Not Selected'
    
    systemVariableObjects= dict_dict_to_zipped_list(SystemVariable.systemVariables,['index','displayName'])  

    challengeObjects=[]     
    chall=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse)
    # Why loop through unassigned problems just to get the last unassigned problem id? (AH)
    for challID in chall:
        unassignID = challID.challengeID   

    challenges = Challenges.objects.filter(courseID=currentCourse)       
    for challenge in challenges:
        # This code will actually append the challenges that are unassigned (except for the last one
        # that we found in the above for loop) along with all other assigned challenges?
        # Are we trying to only get the assigned problems? (AH)
        if challenge.challengeID != unassignID:    
            challengeObjects.append(challenge)
            print("challenge: "+str(challenge))
                
    # The range part is the index numbers.
    context_dict['systemVariables'] = systemVariableObjects
    context_dict['challenges'] = zip(range(1,challenges.count()+1),challengeObjects)
    context_dict['num_Conditions'] = "0";

    return render(request,'Badges/CreateBadge.html', context_dict)

def extractPaths(context_dict): #function used to get the names from the file location
    imagePath = []
    
    for name in glob.glob('static/images/badges/*'):
        name = name.replace("\\","/")
        imagePath.append(name)
        print(name)
    
    context_dict["imagePaths"] = zip(range(1,len(imagePath)+1), imagePath)
