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
    
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,currentCourse = studentInitialContextDict(request)
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:                
        current_course = request.session['currentCourseID']
                      
        categories_list = []
        cats = []
        categories_names = []
          
        studentId = context_dict['student'] #get student
        categories = ActivitiesCategory.objects.filter(courseID=current_course)
        for cat in categories:
            cats.append(cat)
    
        
        #Displaying the list of challenges from database   
        if request.method == "GET" or request.POST.get('actCat') == "all":      
            context_dict['currentCat'] = "all"
            
        elif request.method == "POST":
            filterCategory = request.POST.get('actCat')
            if filterCategory is not None:
                categories = ActivitiesCategory.objects.filter(pk=filterCategory, courseID=current_course)
                context_dict['currentCat'] = categories
            else:
                context_dict['currentCat'] = "all"
            
        for category in categories:
            print("cat name")
            print(category.name)
            cat_activities = category_activities(category, studentId, current_course)
            
            if cat_activities:
                categories_list.append(cat_activities)
                categories_names.append(category.name)
                
        context_dict["categories"]=cats
        context_dict["categories_range"]=zip(categories_list,categories_names)
        
        #make the student activities
        #categories={}
        #activity_categories = ActivitiesCategory.objects.filter( courseID=currentCourse)
        #for act_cat in activity_categories:
        
        
        
            
        # The range part is the index numbers.
        #context_dict['activity_range'] = zip(range(1,len(activities)+1),instructorActivites,studentActivities, points)
        return render(request,'Students/ActivityList.html', context_dict)

    return render(request,'Students/ActivityList.html', context_dict)

def category_activities(category, studentId, current_course):
    
    
    activites = []
    points = []
    activity_points = []
    submit_status=[]
    activity_date_status=[]
    
    activity_objects = Activities.objects.filter(category=category, courseID=current_course)
    print(activity_objects)
    for act in activity_objects:
        # if today is after the data it was assigninged display it 
        #logger.debug(act.startTimestamp)
        #logger.debug(utcDate())
        if act.startTimestamp <= utcDate():
            activites.append(act) # add the activities to the list so we can display
        else: #Today is before the day it is assigend
            continue

        activity_points.append(round(act.points))
        if act.deadLine == None:
            activity_date_status.append("Undated Activity")
        elif act.deadLine < utcDate():
            activity_date_status.append("Past Activity")
        else:
            activity_date_status.append("Upcoming Activity")
        # get the activity record for this student
        if StudentActivities.objects.filter(studentID = studentId, activityID=act):
            student_act = StudentActivities.objects.get(studentID = studentId, activityID=act)
            if student_act.activityScore == -1:
                points.append("-")
            else:
                points.append(str(round(student_act.activityScore)))
            submit_status.append("Submitted")
            
        else:
            
            points.append("-")
            submit_status.append("Missing")
            
            
    return zip(activites,points,activity_points,submit_status,activity_date_status)

    
    
    
