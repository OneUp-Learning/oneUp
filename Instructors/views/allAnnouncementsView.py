'''
Created on Sept 24, 2015

Modified 09/27/2016

@author: Dillon Perry
'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Announcements
from Instructors.views.utils import utcDate, initialContextDict
from datetime import datetime


def createContextForAnnouncementList(currentCourse, context_dict):

    announcement_ID = []      
    author_ID = []
    start_Timestamp = []
    end_Timestamp = []
    subject = []
    message = []
        
    announcements = Announcements.objects.filter(courseID=currentCourse).order_by('-startTimestamp')

    for announcement in announcements:
        announcement_ID.append(announcement.announcementID) #pk
        author_ID.append(announcement.authorID)
        start_Timestamp.append(announcement.startTimestamp)
        end_Timestamp.append(announcement.endTimestamp)
        subject.append(announcement.subject[:25])
        message.append(announcement.message[:300])
    
    removeExpired()
      
    # The range part is the index numbers.
    context_dict['announcement_range'] = zip(range(1,announcements.count()+1),announcement_ID,author_ID,start_Timestamp,end_Timestamp,subject,message)
    return context_dict

    
@login_required
def allAnnouncements(request):

    context_dict, currentCourse = initialContextDict(request)

    return render(request,'Instructors/Announcements.html', context_dict)


#compares current time with the endTimestamp of each announcement
#if the current time exceeds the endTimestamp, the announcement is deleted from the database
def removeExpired():
    announcements = Announcements.objects.all()
    currentTime = utcDate().strftime("%m/%d/%Y %I:%M %p") 
    for announcement in announcements:
        if (currentTime > datetime.strptime(str(announcement.endTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p")):
            announcement.delete()
    
    
