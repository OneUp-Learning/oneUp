'''
Created on Sept 24, 2015

Modified 09/27/2016

@author: Dillon Perry
'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Announcements, Courses
from Students.models import Student, StudentRegisteredCourses

from time import strftime

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

    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict)
        context_dict['course_Name'] = currentCourse.courseName
        student = Student.objects.get(user=request.user)
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage                                 
    else:
        context_dict['course_Name'] = 'Not Selected'

    return render(request,'Students/Announcements.html', context_dict)


#compares current time with the endTimestamp of each announcement
#if the current time exceeds the endTimestamp, the announcement is deleted from the database
def removeExpired():
    announcements = Announcements.objects.all()
    currentTime = strftime("%Y-%m-%d %H:%M:%S")
    for announcement in announcements:
        if (currentTime > announcement.endTimestamp.strftime("%Y-%m-%d %H:%M:%S")):
            announcement.delete()
    
    
