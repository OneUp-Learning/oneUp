'''
Created on Aug 28, 2017

@author: jevans116
'''
from django.shortcuts import render
from Students.models import StudentActivities
from Students.views.utils import studentInitialContextDict
from Instructors.models import Activities
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


from django.contrib.auth.decorators import login_required

@login_required
def ActivityList(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,currentCourse = studentInitialContextDict(request)
    print(context_dict)
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:                
        currentCourse = request.session['currentCourseID']
        instructorActivites = []
        studentActivities = []
                
        studentId = context_dict['student'] #get student
        
        #Displaying the list of challenges from database        
        activities = Activities.objects.filter(courseID=currentCourse)        
        
        #make the student activities
        for act in activities:
            instructorActivites.append(act) # add the activities to the list so we can display
            
            # get the activity record for this student
            try:
                currentActivity =  StudentActivities.objects.get(studentID = studentId, activityID=act)
            except ObjectDoesNotExist:
                currentActivity = None 
                 
            if(currentActivity): #if we got the student activity add it to the list
                studentActivities.append(currentActivity)
                
            else: #make the student activity and add it to he list 
                print('Makeing the activity ' + str(act))
                currentActivity = StudentActivities()
                currentActivity.studentID = studentId
                currentActivity.courseID = act.courseID
                currentActivity.activityID = act
                currentActivity.timestamp = datetime.datetime.now()
                currentActivity.activityScore = 0 
                currentActivity.save()
             
            # The range part is the index numbers.
        context_dict['activity_range'] = zip(range(1,len(activities)+1),instructorActivites,studentActivities)
        return render(request,'Students/ActivityList.html', context_dict)

    return render(request,'Students/ChallengesList.html', context_dict)