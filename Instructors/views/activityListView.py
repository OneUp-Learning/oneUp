'''
Created on March 11, 2015

@author: dichevad
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Activities, Courses, ActivitiesCategory
from Students.models import StudentRegisteredCourses, StudentActivities
from Instructors.views.utils import initialContextDict
from Instructors.constants import uncategorized_activity
from django.template.defaultfilters import default
@login_required
def createContextForActivityList(request):
    
    context_dict, currentCourse = initialContextDict(request)
   
    activity_ID = []      
    activity_Name = []         
    description = []
    points = []
     
    student_ID = []    
    student_Name = []   
    
    if(ActivitiesCategory.objects.filter(name=uncategorized_activity).first() == None):
        defaultCat = ActivitiesCategory()
        defaultCat.name = uncategorized_activity
        defaultCat.courseID = currentCourse
        defaultCat.save() 
      
    if request.method == "GET" or request.POST.get('actCat') == "all":
        activities = Activities.objects.filter(courseID=currentCourse)
        for activity in activities:
            activity_ID.append(activity.activityID) #pk
            activity_Name.append(activity.activityName)
            description.append(activity.description[:100])
            points.append(activity.points)
        context_dict['currentCat'] = "all"
    elif request.method == "POST":
        filterCategory = request.POST.get('actCat')
        if filterCategory is not None:
            category = ActivitiesCategory.objects.get(pk=filterCategory, courseID=currentCourse)
            activities = Activities.objects.filter(category=category, courseID=currentCourse)
            for activity in activities:
                activity_ID.append(activity.activityID) #pk
                activity_Name.append(activity.activityName)
                description.append(activity.description[:100])
                points.append(activity.points)
            context_dict['currentCat'] = category

                    
    # The range part is the index numbers.
    context_dict['activity_range'] = zip(range(1,activities.count()+1),activity_ID,activity_Name,description,points)
    context_dict['activitesForCats'] = zip(range(1,activities.count()+1),activity_ID,activity_Name,description,points)
    
    #Get StudentID and StudentName for every student in the current course
    #This context_dict is used to populate the scrollable check list for student names
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
    for entry in studentCourse:
        student_ID.append(entry.studentID.id)
        student_Name.append((entry.studentID).user.get_full_name())
    context_dict['student_select_range'] = zip(student_ID,student_Name)
    context_dict['activity_select_range'] = zip(activity_ID, activity_Name)
    
    
    
    #Assignment History Section
    assignment_ID = []
    assignment_Name = []
    assignment_Recipient = []
    assignment_Points = []
    
    assignments = StudentActivities.objects.all().order_by('-studentActivityID')
    for assignment in assignments:
        assignment_ID.append(assignment.studentActivityID) #pk
        assignment_Name.append(assignment.activityID.activityName)
        assignment_Recipient.append(assignment.studentID)
        assignment_Points.append(assignment.activityScore)
    context_dict['assignment_history_range'] = zip(range(1,assignments.count()+1),assignment_Name,assignment_Recipient,assignment_Points, assignment_ID)
    
    categories = ActivitiesCategory.objects.filter(courseID=currentCourse)
    context_dict['categories'] =  categories

    return context_dict

    
@login_required
def activityList(request):

    context_dict = createContextForActivityList(request)
        
    
    return render(request,'Instructors/ActivitiesList.html', context_dict)
