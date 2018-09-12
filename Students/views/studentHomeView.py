'''
Created on Sep 20, 2016

'''
from django.shortcuts import render
from Instructors.models import Announcements
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses
from Badges.models import CourseConfigParams
from datetime import datetime
from django.utils import timezone

def StudentHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated    
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        context_dict['avatar'] = anonymous_avatar      #avatar is for a particular course   
        
    # course still not selected
    context_dict['course_Name'] = 'Not Selected'
        
    course_ID = []      
    course_Name = []
    course_available = []

    announcement_ID = []       
    announcement_course = []         
    start_timestamp = []
    subject = []
    message = []
        
    num_announcements = 0
    # get only the courses of the logged in user
    student = Student.objects.get(user=request.user) 
    context_dict['is_test_student'] = student.isTestStudent
    if student.isTestStudent:
        context_dict["username"]="Test Student"
    reg_crs = StudentRegisteredCourses.objects.filter(studentID=student)

    #get today's date
    today = datetime.now(tz=timezone.utc).date()
    for item in reg_crs:
        course = CourseConfigParams.objects.get(courseID=item.courseID.courseID)
        if course.courseStartDate <= today and course.courseEndDate >=today:
            course_ID.append(item.courseID.courseID) 
            course_Name.append(item.courseID.courseName)
            course_available.append(course.courseAvailable)
            course_announcements = Announcements.objects.filter(courseID=item.courseID).order_by('-startTimestamp')
            if not course_announcements.count()==0 and course.courseAvailable:   
                last_course_announc= course_announcements[0]
                announcement_ID.append(last_course_announc.announcementID)       
                announcement_course.append(item.courseID.courseName)         
                start_timestamp.append(last_course_announc.startTimestamp)
                subject.append(last_course_announc.subject[:25])
                message.append(last_course_announc.message[:300])
                num_announcements = num_announcements+1
                    
    context_dict['course_range'] = sorted(list(zip(range(1,reg_crs.count()+1),course_ID,course_Name, course_available)), key=lambda tup: -tup[3])
    context_dict['num_announcements'] = num_announcements
    context_dict['announcement_range'] = zip(range(1,num_announcements+1),announcement_ID,announcement_course,start_timestamp,subject,message)
         
    return render(request,'Students/StudentHome.html', context_dict)