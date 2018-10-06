'''
Created on Aug 28, 2017

@author: jevans116
'''
from django.shortcuts import render
from Students.models import StudentActivities
from Students.views.utils import studentInitialContextDict
from Instructors.models import Activities, ActivitiesCategory
from Instructors.views.utils import utcDate
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


from django.contrib.auth.decorators import login_required
from Badges.systemVariables import logger

@login_required
def ActivityList(request):
    print('Come here')
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
        
        categories = ActivitiesCategory.objects.filter(courseID=currentCourse)
        context_dict['categories'] =  categories
        
        #Displaying the list of challenges from database   
        if request.method == "GET" or request.POST.get('actCat') == "all":      
            activities = Activities.objects.filter(courseID=currentCourse)
            context_dict['currentCat'] = "all"
            
        elif request.method == "POST":
            filterCategory = request.POST.get('actCat')
            if filterCategory is not None:
                category = ActivitiesCategory.objects.get(pk=filterCategory, courseID=currentCourse)
                activities = Activities.objects.filter(category=category, courseID=currentCourse)
                context_dict['currentCat'] = category
            else:
                activities = Activities.objects.filter(courseID=currentCourse)
                context_dict['currentCat'] = "all"

            
        if request.method == "POST":
            print("HERE")  
        
        #make the student activities
        #categories={}
        #activity_categories = ActivitiesCategory.objects.filter( courseID=currentCourse)
        #for act_cat in activity_categories:
            
        submit_status=[]
        activity_date_status=[]
        activity_categories= []
        
        for act in activities:
            # if today is after the data it was assigninged display it 
            #logger.debug(act.startTimestamp)
            #logger.debug(utcDate())
            if act.startTimestamp <= utcDate():
                instructorActivites.append(act) # add the activities to the list so we can display
            else: #Today is before the day it is assigend
                continue

            # get the activity record for this student
            if StudentActivities.objects.filter(studentID = studentId, activityID=act):
                student_act = StudentActivities.objects.get(studentID = studentId, activityID=act)
                if student_act.activityScore == -1:
                    points.append("-")
                else:
                    points.append(str(student_act.activityScore))
                submit_status.append("Submitted")
                if act.deadLine == None:
                    activity_date_status.append("Undated")
                elif act.deadLine < utcDate():
                    activity_date_status.append("Past")
                else:
                    activity_date_status.append("Upcoming")
                
                activity_categories.append([str(act.category.name)])
                    
            else:
                
                points.append("-")
                submit_status.append("Unsubmitted")
                if act.deadLine == None:
                    activity_date_status.append("Undated")
                elif act.deadLine < utcDate():
                    activity_date_status.append("Past")
                else:
                    activity_date_status.append("Upcoming")
                
                activity_categories.append([str(act.category.name)])
                
            studentActivities.append(act)
            
        # The range part is the index numbers.
        context_dict['activity_range'] = zip(range(1,len(activities)+1),instructorActivites,studentActivities, points)
        return render(request,'Students/ActivityList.html', context_dict)

    return render(request,'Students/ActivityList.html', context_dict)
