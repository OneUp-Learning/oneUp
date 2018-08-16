#
# Created on  03/10/2015
# DD
#
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from Instructors.models import Activities, UploadedActivityFiles, ActivitiesCategory
from Instructors.views.utils import utcDate, initialContextDict
from Instructors.constants import default_time_str
from datetime import datetime

@login_required
def activityCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)
    string_attributes = ['activityName','description','points','instructorNotes'];
    actCats = ActivitiesCategory.objects.filter(courseID=currentCourse)
    context_dict['categories'] = actCats
    
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
        
        activity.courseID = currentCourse
        
        if request.POST['actCat']:           
            activity.category = ActivitiesCategory.objects.filter(pk=request.POST['actCat'], courseID=currentCourse).first()
        
        if 'isGraded' in request.POST:
            activity.isGraded = True
        else:
            activity.isGraded = False
            
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
            activity.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
            activity.startTimestamp = utcDate(request.POST['startTime'], "%m/%d/%Y %I:%M %p")
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            activity.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
            if datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M %p"):
                activity.endTimestamp = utcDate(request.POST['endTime'], "%m/%d/%Y %I:%M %p")
            else:
                activity.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
                
        if(request.POST['deadLine'] == ""):
            activity.deadLine = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
            if datetime.strptime(request.POST['deadLine'], "%m/%d/%Y %I:%M %p"):
                activity.deadLine = utcDate(request.POST['deadLine'], "%m/%d/%Y %I:%M %p")
            else:
                activity.deadLine = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")

            
                  
        # get the author                            
        if request.user.is_authenticated():
            activity.author = request.user.username
        else:
            activity.author = ""
            
        activity.save();  #Writes to database.
        
        
        print('Starting Files' + str(len(request.FILES)))
        #Check to see if there are any files that need to be handled and linked to activity
        if len(request.FILES) != 0:
            print('In the file section')
            files =  request.FILES.getlist('actFile')
            makeFilesObjects(request.user, files, activity)
            
        print('End Files')    
         
        return redirect('/oneUp/instructors/activitiesList')

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
                    
                context_dict['currentCat'] = activity.category
                context_dict['categories'] = ActivitiesCategory.objects.filter(courseID=currentCourse)
        
                
                context_dict['uploadAttempts']= activity.uploadAttempts
                context_dict['isFileUpload'] = activity.isFileAllowed
                context_dict['isGraded'] = activity.isGraded
#                 context_dict['startTimestamp']= activity.startTimestamp
#                 context_dict['endTimestamp']= activity.endTimestamp
                
                etime = activity.endTimestamp.strftime("%m/%d/%Y %I:%M %p")
                print('etime ', etime)
                
                if etime != default_time_str: 
                    print('etime2 ', etime)   
                    context_dict['endTimestamp']=etime
                else:
                    context_dict['endTimestamp']=""
                    
                deadTime = activity.deadLine.strftime("%m/%d/%Y %I:%M %p")
                print('deadTime ', deadTime)
                
                if deadTime != default_time_str: 
                    context_dict['deadLineTimestamp']= deadTime
                else:
                    context_dict['deadLineTimestamp']=""
                
            
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
    #oldActFile = UploadedActivityFiles.objects.filter(activityFileCreator=instructorID, activity=activity)

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
        
        
        
        
        
        
