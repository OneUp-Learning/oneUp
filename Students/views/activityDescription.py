'''
Created on Aug 30, 2017

@author: Joel A. Evans
'''
import os
import zipfile
from datetime import date, datetime
from zipfile import ZipFile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.shortcuts import redirect, render
from django.utils import timezone

from Badges.enums import Event
from Badges.events import register_event
from Badges.systemVariables import activityScore
from Instructors.models import Activities, UploadedActivityFiles, UploadedFiles
from Instructors.views.utils import current_localtime, datetime_to_local
from oneUp.settings import MEDIA_ROOT
from Students.models import Student, StudentActivities, StudentFile
from Students.views.utils import studentInitialContextDict

#from requests.api import request


@login_required
def ActivityDetail(request):

    context_dict, currentCourse = studentInitialContextDict(request)

    # Displaying the list of challenges that the student has taken from database
    #studentId = Student.objects.filter(user=request.user)
    studentId = context_dict['student']

    if request.method == 'GET':
        if 'activityID' in request.GET:  # get the activtiy for the student
            context_dict['activityID'] = request.GET['activityID']
            #context_dict['activity'] = StudentActivities.objects.get(pk=request.GET['activityID'])
            #studentActivities = None
            # if StudentActivities.objects.filter(studentID=studentId, courseID=currentCourse, studentActivityID = request.GET['activityID']):
            #stuentActivities = StudentActivities.objects.get(studentID=studentId, courseID=currentCourse, studentActivityID = request.GET['activityID'])

            # If the act has files add them to the webpage
            act = request.GET['activityID']
            activity = Activities.objects.get(activityID=act)

            # Return if the current time is not within window
            if activity.hasStartTimestamp and datetime_to_local(activity.startTimestamp) > current_localtime():
                return redirect('/oneUp/students/ActivityList')
            if activity.hasEndTimestamp and datetime_to_local(activity.endTimestamp) <= current_localtime():
                return redirect('/oneUp/students/ActivityList')

            context_dict['activity'] = activity            
            context_dict['hasDueDate'] = activity.hasDeadline

            instructorActFiles = UploadedActivityFiles.objects.filter(
                activity=activity, latest=True)
            # print(instructorActFiles)
            instructFiles = []

            if instructorActFiles:
                for f in instructorActFiles:
                    instructFiles.append(f.activityFileName)

                context_dict['instructorActFiles'] = instructFiles
                context_dict['instructorHasFiles'] = True
            else:
                context_dict['instructorHasFiles'] = False

            #timeCheck = checkTimes(studentActivities.activityID.endTimestamp, studentActivities.activityID.deadLine)
            if StudentActivities.objects.filter(studentID=studentId, activityID=activity):
                student_activity = StudentActivities.objects.get(
                    studentID=studentId, activityID=activity)

                studentFile = StudentFile.objects.filter(
                    studentID=studentId, activity=student_activity, latest=True)
                context_dict['comment'] = student_activity.comment
                context_dict['isSubmitted'] = student_activity.submitted
                context_dict['submissionTime'] = student_activity.submissionTimestamp
                context_dict['isGraded'] = activity.isGraded
                if student_activity.graded:
                    context_dict['score'] = student_activity.activityScore
                    context_dict['bonus'] = student_activity.bonusPointsAwarded
                else:
                    context_dict['score'] = "-"
                    context_dict['bonus'] = "-"
                context_dict['feedback'] = student_activity.instructorFeedback
                
                if student_activity.submitted:
                    if activity.hasDeadline and datetime_to_local(student_activity.submissionTimestamp) > datetime_to_local(activity.deadLine):
                        context_dict['submit_status'] = "Late Submission"
                    else:
                        context_dict['submit_status'] = "Submitted"

                # we are allowed to upload files
                if activity.isFileAllowed == True and (not isDisplayTimePassed(datetime_to_local(activity.endTimestamp)) or not activity.hasEndTimestamp):
                    if student_activity.graded or (studentFile and student_activity.numOfUploads >= activity.uploadAttempts):
                        context_dict['canUpload'] = False
                    else:
                        context_dict['canUpload'] = True

                else:  # not allowed to upload files
                    context_dict['canUpload'] = False
                
                fileName = getUploadedFileNames(studentFile)
                context_dict['fileName'] = fileName

            else:
                if activity.isFileAllowed == True and (not isDisplayTimePassed(datetime_to_local(activity.endTimestamp)) or not activity.hasEndTimestamp):
                    context_dict['canUpload'] = True
                else:
                    context_dict['canUpload'] = False

                context_dict['isSubmitted'] = False
                context_dict['score'] = "-"
                context_dict['bonus'] = "-"
                context_dict['feedback'] = ""
                context_dict['isGraded'] = False
        else:
            return redirect('/oneUp/students/ActivityList')

    elif request.method == 'POST':
        # print(len(request.FILES.getlist('actFile')))

        files = []

        for currentFile in request.FILES.getlist('actFile'):
                # print(currentFile.name)
            files.append(currentFile)

        activity = Activities.objects.get(
            activityID=request.POST['activityID'], courseID=currentCourse)
        if StudentActivities.objects.filter(activityID=activity, studentID=studentId, courseID=currentCourse):
            student_activity = StudentActivities.objects.get(
                activityID=activity, studentID=studentId, courseID=currentCourse)
            student_activity.comment = request.POST['comment']
            student_activity.submissionTimestamp = current_localtime()
            student_activity.submitted = True

            if files:
                student_activity.numOfUploads += 1

            student_activity.save()

        else:
            student_activity = StudentActivities()
            student_activity.studentID = studentId
            student_activity.activityID = activity
            student_activity.courseID = currentCourse
            student_activity.activityScore = 0
            student_activity.submissionTimestamp = current_localtime()
            student_activity.submitted = True
            student_activity.comment = request.POST['comment']
            if files:
                student_activity.numOfUploads = 1
            else:
                student_activity.numOfUploads = 0
            student_activity.save()

        if files:
            fileName = makeFileObjects(
                studentId, currentCourse, files, student_activity)

        register_event(Event.activitySubmission, request,
                        studentId, activity.activityID)

        return redirect('/oneUp/students/ActivityList')

    return render(request, 'Students/ActivityDescription.html', context_dict)


def makeFileObjects(studentId, currentCourse, files, studentActivities):
    fileNames = []

    oldStudentFile = StudentFile.objects.filter(
        studentID=studentId, activity=studentActivities)
    for f in oldStudentFile:
        f.latest = False
        f.save()

    # When given multiple files we zip them together
    filesForZip = []

    if(len(files) == 1):  # if there is one file make just save it
        studentFile = StudentFile()
        studentFile.studentID = studentId
        studentFile.courseID = currentCourse
        studentFile.file = files[0]
        studentFile.fileName = files[0].name
        studentFile.activity = studentActivities
        studentFile.save()
        studentFile.fileName = os.path.basename(studentFile.file.name)
        studentFile.save()
        fileNames.append(files[0].name)

    else:  # if there is more than one file save them and zip together

        for i in range(0, len(files)):  # make student files so we can save files to hardrive
            studentFile = StudentFile()
            studentFile.studentID = studentId
            studentFile.courseID = currentCourse
            studentFile.file = files[i]
            studentFile.fileName = files[i].name
            studentFile.activity = studentActivities
            studentFile.save()
            filesForZip.append(studentFile)
            fileNames.append(files[i].name)

        # make zip file
        firstName = studentId.user.first_name
        lastName = studentId.user.last_name
        activityName = studentActivities.activityID.activityName
        zipName = firstName + lastName + activityName + '.zip'
        zipPath = os.path.join(os.path.join(os.path.abspath(
            MEDIA_ROOT), 'studentActivities'), zipName)

        zipFile = ZipFile(zipPath, "w")

        for objects in filesForZip:
            filePath = objects.file.name
            zipFile.write(filePath)

        zipFile.close()

        # link zip to an object
        studentFile = StudentFile()
        studentFile.studentID = studentId
        studentFile.courseID = currentCourse
        studentFile.file = File(open(zipPath, "rb"))
        studentFile.fileName = zipName
        studentFile.activity = studentActivities
        studentFile.save()

        # delete oldFile objects
        for object in filesForZip:
            object.delete()

        for ob in oldStudentFile:
            ob.delete()

        return fileNames


def isDisplayTimePassed(endTimeStamp):
    return endTimeStamp < current_localtime()

def checkTimes(endTimestamp, deadLine):

    endMax = max((endTimestamp, current_localtime()))
    deadMax = max((deadLine, current_localtim()))

    if(endMax == endMax and deadMax == deadLine):
        return True
    else:
        return False


def getUploadedFileNames(studentFile):
    fileName = []
    for file in studentFile:
        path = file.file.name
        name = os.path.basename(path)
        # if zip file get all the files inside the zip
        if(zipfile.is_zipfile(path)):
            with ZipFile(path, 'r') as zip:
                zipNames = zip.namelist()
                for z in zipNames:
                    fileName.append(os.path.basename(z))
        else:
            fileName.append(name)
    return fileName
