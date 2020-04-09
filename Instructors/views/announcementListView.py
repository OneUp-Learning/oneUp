'''
Created on Sept 24, 2015

Modified 09/27/2016

@author: Dillon Perry
'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Announcements, Instructors, Courses
from Instructors.views.utils import localizedDate, initialContextDict, str_datetime_to_local, current_localtime, datetime_to_selected
from datetime import datetime
from oneUp.decorators import instructorsCheck   
from django.utils import timezone

# Added boolean to check if viewing from announcements page or course home page
def createContextForAnnouncementList(currentCourse, context_dict, courseHome):

    announcement_ID = []      
    author_ID = []
    start_Timestamp = []
    end_Timestamp = []
    subject = []
    message = []
        
    announcements = Announcements.objects.filter(courseID=currentCourse).order_by('-startTimestamp')
    removeExpired()
    index = 0
    if not courseHome: # Shows all the announcements
        for announcement in announcements:
            announcement_ID.append(announcement.announcementID) #pk
            author_ID.append(announcement.authorID)
            # Announcement will also show startTime (created time)
            start_Timestamp.append(announcement.startTimestamp)

            if announcement.hasEndTimestamp: 
                # For displaying the local datetime in a different format do this
                endTime = announcement.endTimestamp
                print(endTime)
                print(announcement.endTimestamp)
                print(timezone.localtime(announcement.endTimestamp))
                end_Timestamp.append(datetime_to_selected(endTime))
            else:
                end_Timestamp.append("")
            
            subject.append(announcement.subject[:25])
            message.append(announcement.message[:300])
    else: # Only shows the first three
        for announcement in announcements:
            if index < 1:
                announcement_ID.append(announcement.announcementID) #pk
                author_ID.append(announcement.authorID)
                start_Timestamp.append(announcement.startTimestamp)
                end_Timestamp.append(announcement.endTimestamp)
                subject.append(announcement.subject[:25])
                message.append(announcement.message[:300])
                index += 1
    
      
    # The range part is the index numbers.
    context_dict['announcement_range'] = zip(range(1,announcements.count()+1),announcement_ID,author_ID,start_Timestamp,end_Timestamp,subject,message)
    return context_dict

    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def announcementList(request):

    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForAnnouncementList(currentCourse, context_dict, False)
    
    return render(request,'Instructors/AnnouncementsList.html', context_dict)


#compares current time with the endTimestamp of each announcement
#if the current time exceeds the endTimestamp, the announcement is deleted from the database
def removeExpired():
    announcements = Announcements.objects.all()
    currentTime = current_localtime()
    for announcement in announcements:
        if announcement.hasEndTimestamp and currentTime > announcement.endTimestamp:
            announcement.delete()
            
    
    
