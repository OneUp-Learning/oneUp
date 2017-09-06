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
            
            #we are allowed to uplad files 
            if(studentActivities.activityID.isFileAllowed == True):
                context_dict['canUpload'] = True
                #Check and see if the activity file has already been uplaoded
                studentFile = StudentFile.objects.filter(studentID=studentId, activity=studentActivities )
                if studentFile:
                   isFile = True
                   fileName = []
                   for file in studentFile:
                    fileName.append(file.fileName)
                    context_dict['fileName'] = fileName
                else:
                    isFile = False
                
                print(isFile)
                
                context_dict['isFile'] = isFile
                
            else: #not allowed to upload files 
                context_dict['canUpload'] = False

                
                  
        
        if request.POST and len(request.FILES) > 0 : #means that we are tryng to upload some activty 
            #print(len(request.FILES.getlist('actFile')))
            
            files = []
            
            for currentFile in request.FILES.getlist('actFile'):
                    #print(currentFile.name)
                    files.append(currentFile)
                          
            studentActivities = StudentActivities.objects.get(studentID=studentId, courseID=currentCourse, studentActivityID = request.POST['studentActivity'])
            makeFileObjects(studentId, currentCourse, files, studentActivities)
            context_dict['files'] = files
                    
            return redirect('/oneUp/students/ActivityList', context_dict)
        return render(request,'Students/ActivityDescription.html', context_dict)

def makeFileObjects(studentId, currentCourse,files, studentActivities):
    #Like the file to the student
    for i in range(0, len(files)):
        studentFile = StudentFile()
        studentFile.studentID = studentId
        studentFile.courseID = currentCourse
        studentFile.file = files[i]
        studentFile.fileName = files[i].name
        studentFile.activity = studentActivities
        studentFile.save()
            