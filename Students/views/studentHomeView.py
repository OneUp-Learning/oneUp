'''
Created on Sep 20, 2016

'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Courses, Announcements
from Students.models import Student, StudentRegisteredCourses

def StudentHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()    
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    # course still not selected
    context_dict['course_Name'] = 'Not Selected'
        
    course_ID = []      
    course_Name = []

    announcement_ID = []       
    announcement_course = []         
    start_timestamp = []
    subject = []
    message = []
        
    num_announcements = 0
    # get only the courses of the logged in user
    student = Student.objects.get(user=request.user)   
    reg_crs = StudentRegisteredCourses.objects.filter(studentID=student)
   # print(reg_crs)
    for item in reg_crs:
        course_ID.append(item.courseID.courseID) 
        course_Name.append(item.courseID.courseName)
        course_announcements = Announcements.objects.filter(courseID=item.courseID).order_by('-startTimestamp')
        if not course_announcements.count()==0:   
            last_course_announc= course_announcements[0]
            announcement_ID.append(last_course_announc.announcementID)       
            announcement_course.append(item.courseID.courseName)         
            start_timestamp.append(last_course_announc.startTimestamp)
            subject.append(last_course_announc.subject[:25])
            message.append(last_course_announc.message[:300])
            num_announcements = num_announcements+1
                    
    context_dict['course_range'] = zip(range(1,reg_crs.count()+1),course_ID,course_Name)
    context_dict['num_announcements'] = num_announcements
    context_dict['announcement_range'] = zip(range(1,num_announcements+1),announcement_ID,announcement_course,start_timestamp,subject,message)
         
    return render(request,'Students/StudentHome.html', context_dict)