'''
Created on Mar 21, 2018

@author: oumar
'''
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from Instructors.models import Activities
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Students.models import Student, StudentActivities, User


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def activityScore(request):

    context_dict, currentCourse = initialContextDict(request)
    
    if 'userID' in request.GET:
        stud = User.objects.get(username=request.GET['userID'])
        studentID = Student.objects.get(user=stud)

        context_dict['student'] = stud.last_name
        points = []
        bonus = []
        maxPoints = []
        activityNames = []
        feedbacks = []
        
        
        #studentId = context_dict['student'] #get student
        
        #Displaying the list of challenges from database        
        activities = Activities.objects.filter(courseID=currentCourse)     
        
        for activity in activities:
            activityNames.append(activity.activityName)
            maxPoints.append(activity.points)
            
            if StudentActivities.objects.filter(courseID=currentCourse, studentID=studentID, activityID=activity):
                
                studentActivity =  StudentActivities.objects.get(studentID = studentID, activityID=activity)
                points.append(studentActivity.activityScore)
                bonus.append(studentActivity.bonusPointsAwarded)
                feedbacks.append(studentActivity.instructorFeedback)
            
            else: 
                points.append("-")
                bonus.append("-")
                feedbacks.append("")
            
        context_dict['activity_range'] = zip(activityNames,maxPoints,points, bonus, feedbacks)           
    
    return render(request,'Instructors/ActivityScoreForm.html', context_dict)
