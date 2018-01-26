#
# Created on  03/10/2015
# DD
#
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Activities, Courses
from Instructors.views.activityListView import createContextForActivityList
from Instructors.views.utils import utcDate, initialContextDict
from Instructors.constants import unspecified_topic_name, default_time_str
from time import time
from datetime import datetime
@login_required
def activityCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)
    string_attributes = ['activityName','description','points','instructorNotes'];
    
    
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
            
                  
       # get the author                            
        if request.user.is_authenticated():
            activity.author = request.user.username
        else:
            activity.author = ""

        activity.save();  #Writes to database.
         
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
                
                context_dict['uploadAttempts']= activity.uploadAttempts
                context_dict['isFileUpload'] = activity.isFileAllowed
#                 context_dict['startTimestamp']= activity.startTimestamp
#                 context_dict['endTimestamp']= activity.endTimestamp
                
                etime = datetime.strptime(str(activity.endTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p")
                print('etime ', etime)
                if etime != default_time_str: 
                    print('etime2 ', etime)   
                    context_dict['endTimestamp']=etime
                else:
                    context_dict['endTimestamp']=""
            
                print(activity.startTimestamp.strftime("%Y")) 
                if activity.startTimestamp.strftime("%Y") < ("2900"):
                    context_dict['startTimestamp']= datetime.strptime(str(getattr(activity, 'startTimestamp')), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p")
                else:
                    context_dict['startTimestamp']=""


    return render(request,'Instructors/ActivityCreateForm.html', context_dict)
