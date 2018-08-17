#
# Created on  09/24/2015
# Dillon Perry
#
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from Instructors.models import Announcements, Courses
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.utils import utcDate, localizedDate, initialContextDict
from Instructors.constants import default_time_str
from datetime import datetime
from notify.signals import notify
from Students.models import StudentRegisteredCourses

@login_required
def announcementCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['subject','message']
    
        
    # prepare context for Announcement List      
    context_dict = createContextForAnnouncementList(currentCourse, context_dict, False) 

    if request.POST:

        # Get the activity from the DB for editing or create a new announcement  
        if 'announcementID' in request.POST:
            ai = request.POST['announcementID']
            announcement = Announcements.objects.get(pk=int(ai))
        else:
            announcement = Announcements()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(announcement,attr,request.POST[attr])
            
                   
       # get the author                            
        if request.user.is_authenticated:
            announcement.authorID = request.user
        else:
            announcement.author = "This Should Not Exist" #We don't think this code should ever run
        
        announcement.courseID = currentCourse 
    
        announcement.startTimestamp = utcDate()
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            announcement.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
            announcement.endTimestamp = localizedDate(request, request.POST['endTime'], "%m/%d/%Y %I:%M %p") 
        
            
        announcement.save();  #Writes to database.
    
                
        return redirect('announcementListView')

    ######################################
    # request.GET 
    else:
        if request.GET:
                            
            # If announcementId is specified then we load for editing.
            if 'announcementID' in request.GET:
                announcement = Announcements.objects.get(pk=int(request.GET['announcementID']))
                
                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['announcementID'] = request.GET['announcementID']
                
                for attr in string_attributes:
                    context_dict[attr]=getattr(announcement,attr)

                # if default end date (= unlimited) is stored, we don't want to display it on the webpage                   
                endTime = announcement.endTimestamp.strftime("%m/%d/%Y %I:%M %p")
                if endTime != default_time_str: 
                    context_dict['endTimestamp']= endTime
                else:
                    context_dict['endTimestamp']= ""
 
    
                

    return render(request,'Instructors/AnnouncementCreateForm.html', context_dict)
