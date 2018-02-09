#
# Created on  03/10/2015
# DD
#
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from Instructors.models import Activities, Courses, UploadedActivityFiles
from Instructors.views.activityListView import createContextForActivityList
from Instructors.views.utils import utcDate
from Instructors.constants import unspecified_topic_name, default_time_str
from time import time
from datetime import datetime
import filecmp
from lib2to3.fixer_util import String
from ckeditor_uploader.views import upload
from notify.signals import notify
from Students.models import StudentRegisteredCourses

@login_required
def activityCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    string_attributes = ['activityName','description','points','instructorNotes'];
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    
    if request.POST:

        # Get the activity from the DB for editing or create a new activity  
        if 'activityID' in request.POST:
            ai = request.POST['activityID']
            activity = Activities.objects.get(pk=int(ai))
        else:
            activity = Activities()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(activity,attr,request.POST[attr])
        
        activity.courseID = currentCourse; 
        if 'fileUpload' in request.POST:
            activity.isFileAllowed = True
        else:
            activity.isFileAllowed = False
            
        #Set the number of attempts
        if 'attempts' in request.POST:
            print(request.POST['attempts'])
            activity.uploadAttempts = request.POST['attempts']
            
        #Set the start date and end data to show the activity
        if(request.POST['startTime'] == ""):
            activity.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        else:
            activity.startTimestamp = utcDate(request.POST['startTime'], "%m/%d/%Y %I:%M %p")
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            activity.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        else:
            if datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M %p"):
                activity.endTimestamp = utcDate(request.POST['endTime'], "%m/%d/%Y %I:%M %p")
            else:
                activity.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
            
                  
       # get the author                            
        if request.user.is_authenticated():
            activity.author = request.user.username
        else:
            activity.author = ""
            
        activity.save();  #Writes to database.
        
        
        #Send Notifications to the students
        studentQuery = StudentRegisteredCourses.objects.filter(courseID = currentCourse)
        students = []
        for s in studentQuery:
            students.append(s.studentID.user)
        
        students = list(students)
        actName = request.POST.get('activityName')
                        
        notify.send(None, recipient_list=students, actor=request.user,
                verb='A new activity '+actName+' has been posted', nf_type='New Activity')
        
        
        
        print('Starting Files' + str(len(request.FILES)))
        #Check to see if there are any files that need to be handled and linked to activity
        if len(request.FILES) != 0:
            print('In the file section')
            files =  request.FILES.getlist('actFile')
            makeFilesObjects(request.user, files, activity)
            
        print('End Files')    
         
        # prepare context for Activity List      
        context_dict = createContextForActivityList(request) 

        context_dict["logged_in"]=request.user.is_authenticated()
        if request.user.is_authenticated():
            context_dict["username"]=request.user.username
                
        return render(request,'Instructors/ActivitiesList.html', context_dict)

    ######################################
    # request.GET 
    else:
        if request.GET:
                            
            # If questionId is specified then we load for editing.
            if 'activityID' in request.GET:
                activity = Activities.objects.get(pk=int(request.GET['activityID']))

                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['activityID'] = request.GET['activityID']
                for attr in string_attributes:
                    context_dict[attr]=getattr(activity,attr)
                
                context_dict['uploadAttempts']= activity.uploadAttempts
                context_dict['isFileUpload'] = activity.isFileAllowed
#                 context_dict['startTimestamp']= activity.startTimestamp
#                 context_dict['endTimestamp']= activity.endTimestamp
                
                etime = activity.endTimestamp.strftime("%m/%d/%Y %I:%M %p")
                print('etime ', etime)
                if etime != default_time_str: 
                    print('etime2 ', etime)   
                    context_dict['endTimestamp']=etime
                else:
                    context_dict['endTimestamp']=""
            
                print(activity.startTimestamp.strftime("%Y")) 
                if activity.startTimestamp.strftime("%Y") < ("2900"):
                    context_dict['startTimestamp']= activity.startTimestamp.strftime("%m/%d/%Y %I:%M %p")
                else:
                    context_dict['startTimestamp']=""
                    
                
                activityFiles =UploadedActivityFiles.objects.filter(activity=activity, latest=True)
                if(activityFiles):
                    context_dict['activityFiles'] = activityFiles
                else:
                    print('No activity files found')

    return render(request,'Instructors/ActivityCreateForm.html', context_dict)

def makeFilesObjects(instructorID, files, activity):
    
    #Get the old files and see if any of the new files match it
    oldActFile = UploadedActivityFiles.objects.filter(activityFileCreator=instructorID, activity=activity)

    for i in range(0, len(files)): #make student files so we can save files to hardrive
        print('Makeing file object' + str(files[i].name))
        actFile = UploadedActivityFiles()
        actFile.activity = activity
        actFile.activityFile = files[i]
        actFile.activityFileName = files[i].name
        actFile.activityFileCreator = instructorID
        actFile.save()
        
def removeFileFromActivty(request):
    if request.user.is_authenticated():
        print('IS A USER')
    else:
        return HttpResponse(403)
    
    if request.POST:
        if 'fileID' in request.POST:
            fID = request.POST['fileID']
            currentFile = UploadedActivityFiles.objects.get(ID=fID)
            currentFile.activityFile.delete()
            currentFile.delete()
            print('File deleted')
            return HttpResponse(200)
        
    return HttpResponse(403, 'something went wrong')        
        
        
        
        
        
        
