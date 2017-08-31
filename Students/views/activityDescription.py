'''
Created on Aug 30, 2017

@author: Joel A. Evans
'''

from django.shortcuts import render, redirect
from Instructors.models import Activities, UploadedFiles
from Students.models import StudentActivities, Student, StudentFile
from Students.views.utils import studentInitialContextDict
from datetime import datetime
from django.contrib.auth.decorators import login_required
from Badges.systemVariables import activityScore
from django.core.exceptions import ObjectDoesNotExist
#from requests.api import request

@login_required
def ActivityDetail(request):
    
    context_dict,currentCourse = studentInitialContextDict(request)
 
    if 'currentCourseID' in request.session:         
        #Displaying the list of challenges that the student has taken from database
        #studentId = Student.objects.filter(user=request.user)
        studentId = context_dict['student']
        
        if 'activityID' in request.GET: #get the activtiy for the student
            context_dict['activityID'] = request.GET['activityID']
            context_dict['activity'] = StudentActivities.objects.get(pk=request.GET['activityID'])
            studentActivities = StudentActivities.objects.get(studentID=studentId, courseID=currentCourse, studentActivityID = request.GET['activityID'])
            
            #Check and see if the activity file has already been uplaoded
            try:
               studentFile = StudentFile.objects.get(studentID=studentId, activity=studentActivities )
               isFile = True
               fileName = studentFile.fileName
               context_dict['fileName'] = fileName
            except ObjectDoesNotExist: #this means that we didn't get the object so its not in DB
                isFile = False
            
            print(isFile)
            
            context_dict['isFile'] = isFile
                  
        
        if request.POST and len(request.FILES) != 0 : #means that we are tryng to upload some activty 
            file = request.FILES['actFile']
            studentActivities = StudentActivities.objects.get(studentID=studentId, courseID=currentCourse, studentActivityID = request.POST['studentActivity'])
                      
            #Like the file to the student
            studentFile = StudentFile()
            studentFile.studentID = studentId
            studentFile.courseID = currentCourse
            studentFile.file = file
            studentFile.fileName = file.name
            studentFile.activity = studentActivities
            studentFile.save()
            
                
            return redirect('/oneUp/students/ActivityList', context_dict)
        return render(request,'Students/ActivityDescription.html', context_dict)

            