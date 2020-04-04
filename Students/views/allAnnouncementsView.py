'''
Created on Sept 24, 2015

Modified 09/27/2016

@author: Dillon Perry
'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Announcements
from Students.views.utils import studentInitialContextDict
from Instructors.views.announcementListView import removeExpired
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

    context_dict,currentCourse = studentInitialContextDict(request)
    context_dict = createContextForAnnouncementList(currentCourse, context_dict)

    return render(request,'Students/Announcements.html', context_dict)
    
    
