'''
Created on Sept 24, 2015

Modified 09/27/2016

@author: Dillon Perry
'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Announcements, Instructors, Courses, Goals
from Instructors.views.utils import utcDate, initialContextDict
from Instructors.constants import default_time_str
from datetime import datetime
from oneUp.decorators import instructorsCheck   
from Students.models import StudentGoalSetting

# Added boolean to check if viewing from announcements page or course home page
def createContextForAnnouncementList(currentCourse, context_dict, courseHome):

    announcement_ID = []      
    author_ID = []
    start_Timestamp = []
    end_Timestamp = []
    subject = []
    message = []
        
    Goals = StudentGoalSetting.objects.filter(courseID=currentCourse).order_by('-startTimestamp')
    removeExpired()
    index = 0
    if not courseHome: # Shows all the announcements
        for announcement in announcements:
            announcement_ID.append(announcement.announcementID) #pk
            author_ID.append(announcement.authorID)
            start_Timestamp.append(announcement.startTimestamp)
            # if default end date (= unlimited) is stored, we don't want to display it on the webpage                   
            endTime = announcement.endTimestamp.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p")
            if endTime != default_time_str: 
                end_Timestamp.append(announcement.endTimestamp)
            else:
                end_Timestamp.append("")
            
            subject.append(announcement.subject[:25])
            message.append(announcement.message[:300])
    else: # Only shows the first three
        for announcement in announcements:
            if index < 3:
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
    currentTime = utcDate().strftime("%m/%d/%Y %I:%M %p") 
    for announcement in announcements:
        if (currentTime > datetime.strptime(str(announcement.endTimestamp.replace(microsecond=0)), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p")):
            announcement.delete()
            
    
    
