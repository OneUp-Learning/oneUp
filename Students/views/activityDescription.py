'''
Created on Aug 30, 2017

@author: Joel A. Evans
'''
import os
from django.core.files import File
from oneUp.settings import MEDIA_ROOT
from zipfile import ZipFile
from django.shortcuts import render, redirect
from Instructors.models import Activities, UploadedFiles, UploadedActivityFiles
from Students.models import StudentActivities, Student, StudentFile
from Students.views.utils import studentInitialContextDict
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from Badges.systemVariables import activityScore
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from Instructors.views.utils import utcDate
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
            
            #If the act has files add them to the webpage
            act = studentActivities.activityID
            instructorActFiles = UploadedActivityFiles.objects.filter(activity=act, latest=True )
            instructFiles = []
            
            if(instructorActFiles):
                for f in instructorActFiles:
                    instructFiles.append(f.activityFileName)
                
                context_dict['instructorActFiles'] = instructFiles
                context_dict['instructorHasFiles'] = True
            else:
                context_dict['instructorHasFiles'] = False
                
            timeCheck = checkTimes(studentActivities.activityID.endTimestamp, studentActivities.activityID.deadLine)
       
            #we are allowed to uplad files 
            if(studentActivities.activityID.isFileAllowed == True and timeCheck):                
                context_dict['canUpload'] = True
                 
                #Check and see if the activity file has already been uplaoded
                studentFile = StudentFile.objects.filter(studentID=studentId, activity=studentActivities, latest=True )
                
                if(studentActivities.graded):
                    isFile = True
                    fileName = []
                    for file in studentFile:
                        name = os.path.basename(file.file.name)
                        fileName.append(name)
                    context_dict['fileName'] = fileName
                else:
                    
                    #if you upload a file and you are out of uploads
                    if studentFile and studentActivities.activityID.uploadAttempts == studentActivities.numOfUploads:
                       isFile = True
                       fileName = []
                       for file in studentFile:
                        name = os.path.basename(file.file.name)
                        fileName.append(name)
                        context_dict['fileName'] = fileName
                        
                    #uploaded a file but can still add more files    
                    elif studentFile and studentActivities.numOfUploads < studentActivities.activityID.uploadAttempts:
                        isFile = False
                        fileName = []
                        for file in studentFile:
                            fileName.append(file.fileName)
                            context_dict['fileName'] = fileName
                             
                    #You haven't uploaded a file
                    else:
                        isFile = False
                
                context_dict['isFile'] = isFile
                
            else: #not allowed to upload files 
                context_dict['canUpload'] = False

                
                  
        
        if request.POST and len(request.FILES) > 0 : #means that we are tryng to upload some files 
            #print(len(request.FILES.getlist('actFile')))
            
            files = []
            
            for currentFile in request.FILES.getlist('actFile'):
                    #print(currentFile.name)
                    files.append(currentFile)
                          
            studentActivities = StudentActivities.objects.get(studentID=studentId, courseID=currentCourse, studentActivityID = request.POST['studentActivity'])
            makeFileObjects(studentId, currentCourse, files, studentActivities)
            
            print(studentActivities.numOfUploads)
            studentActivities.numOfUploads = studentActivities.numOfUploads + 1
            studentActivities.save()
            print(studentActivities.numOfUploads)

            
            context_dict['files'] = files
                    
            return redirect('/oneUp/students/ActivityList', context_dict)
            
        return render(request,'Students/ActivityDescription.html', context_dict)

def makeFileObjects(studentId, currentCourse,files, studentActivities):
    
    oldStudentFile = StudentFile.objects.filter(studentID=studentId, activity=studentActivities)
    for f in oldStudentFile:
        f.latest = False
        f.save()

    
    #When given multiple files we zip them together
    filesForZip = []
    
    if(len(files) == 1): #if there is one file make just save it 
        studentFile = StudentFile()
        studentFile.studentID = studentId
        studentFile.courseID = currentCourse
        studentFile.file = files[0]
        studentFile.fileName = files[0].name
        studentFile.activity = studentActivities
        studentFile.save()
        studentFile.fileName = os.path.basename(studentFile.file.name) 
        studentFile.save()

    
    else: #if there is more than one file save them and zip together
        
        for i in range(0, len(files)): #make student files so we can save files to hardrive
            studentFile = StudentFile()
            studentFile.studentID = studentId
            studentFile.courseID = currentCourse
            studentFile.file = files[i]
            studentFile.fileName = files[i].name
            studentFile.activity = studentActivities
            studentFile.save()
            filesForZip.append(studentFile)
        
        
        #make zip file
        firstName =studentId.user.first_name
        lastName = studentId.user.last_name
        activityName = studentActivities.activityID.activityName
        zipName = firstName + lastName + activityName + '.zip'
        zipPath = os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'studentActivities'),zipName)
        
        zipFile = ZipFile(zipPath, "w")
        
        for objects in filesForZip:
            filePath = objects.file.name
            zipFile.write(filePath)
        
        zipFile.close()
        
        #link zip to an object
        studentFile = StudentFile()
        studentFile.studentID = studentId
        studentFile.courseID = currentCourse
        studentFile.file = File(open(zipPath, "rb"))
        studentFile.fileName = zipName
        studentFile.activity = studentActivities
        studentFile.save()
        
        #delete oldFile objects
        for object in filesForZip:
            object.delete()

def checkTimes(endTimestamp, deadLine):
    print("End" + str(endTimestamp))
    print("dead" + str(deadLine))
    utcNow = utcDate(datetime.now().strftime("%m/%d/%Y %I:%M %p"), "%m/%d/%Y %I:%M %p")
    print("Utc" + str(utcNow))
    endMax = max((endTimestamp, utcNow))
    deadMax = max((deadLine, utcNow))
    
    if(endMax == endMax and deadMax == deadLine):
        return True
    else:
        return False  
          