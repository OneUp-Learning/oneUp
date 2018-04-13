'''
Created on Aug 28, 2017

@author: jevans116
'''
from django.shortcuts import render
from Students.models import StudentActivities
from Students.views.utils import studentInitialContextDict
from Instructors.models import Activities
from Instructors.views.utils import utcDate
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


from django.contrib.auth.decorators import login_required
from Badges.systemVariables import logger

@login_required
def ActivityList(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,currentCourse = studentInitialContextDict(request)
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:                
        currentCourse = request.session['currentCourseID']
        instructorActivites = []
        studentActivities = []
        points = []
        attempts = []
                
        studentId = context_dict['student'] #get student
        
        #Displaying the list of challenges from database        
        activities = Activities.objects.filter(courseID=currentCourse)  
        
        #make the student activities
        for act in activities:
            
            # if today is after the data it was assigninged display it 
            #logger.debug(act.startTimestamp)
            #logger.debug(utcDate())
            if act.startTimestamp <= utcDate():
                instructorActivites.append(act) # add the activities to the list so we can display
            else: #Today is before the day it is assigend
                continue

                
            
            # get the activity record for this student
            try:
                currentActivity =  StudentActivities.objects.get(studentID = studentId, activityID=act)
                print('Made an ACT')
            except ObjectDoesNotExist:
                currentActivity = None
                print('Not ACT') 
                 
            if(currentActivity): #if we got the student activity add it to the list
                studentActivities.append(currentActivity)
        
                
                if(currentActivity.activityScore == 0 and currentActivity.graded == False):
                    points.append("-")
                else:
                    points.append(str(currentActivity.activityScore))
                
            else: #make the student activity and add it to he list 
                print('Makeing the activity ' + str(act))
                currentActivity = StudentActivities()
                currentActivity.studentID = studentId
                currentActivity.courseID = act.courseID
                currentActivity.activityID = act
                currentActivity.timestamp = utcDate()
                currentActivity.activityScore = 0 
                currentActivity.save()
                
                studentActivities.append(currentActivity)
                if(currentActivity.activityScore == 0 and currentActivity.graded == False):
                    points.append("-")
                else:
                    points.append(str(currentActivity.activityScore))
                
         # The range part is the index numbers.
        context_dict['activity_range'] = zip(range(1,len(activities)+1),instructorActivites,studentActivities, points)
        return render(request,'Students/ActivityList.html', context_dict)

    return render(request,'Students/ActivityList.html', context_dict)
