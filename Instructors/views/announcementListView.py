'''
Created on Sept 24, 2015

Modified 09/27/2016

@author: Dillon Perry
'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Announcements, Instructors, Courses
from Instructors.views.utils import utcDate
from datetime import datetime

def insert_newlines(string, every=10):
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)

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
            start_Timestamp.append(announcement.startTimestamp)
            end_Timestamp.append(announcement.endTimestamp)
            subject.append(announcement.subject[:25])
            message.append(insert_newlines(announcement.message[:300]))
    else: # Only shows the first three
        for announcement in announcements:
            if index < 3:
                announcement_ID.append(announcement.announcementID) #pk
                author_ID.append(announcement.authorID)
                start_Timestamp.append(announcement.startTimestamp)
                end_Timestamp.append(announcement.endTimestamp)
                subject.append(announcement.subject[:25])
                message.append(insert_newlines(announcement.message[:300]))
                index += 1
    
      
    # The range part is the index numbers.
    context_dict['announcement_range'] = zip(range(1,announcements.count()+1),announcement_ID,author_ID,start_Timestamp,end_Timestamp,subject,message)
    return context_dict

    
@login_required
def announcementList(request):

    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict, False)
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'

    return render(request,'Instructors/AnnouncementsList.html', context_dict)


#compares current time with the endTimestamp of each announcement
#if the current time exceeds the endTimestamp, the announcement is deleted from the database
def removeExpired():
    announcements = Announcements.objects.all()
    currentTime = utcDate().strftime("%m/%d/%Y %I:%M %p") 
    for announcement in announcements:
        if (currentTime > datetime.strptime(str(announcement.endTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p")):
            announcement.delete()
            
    
    
