'''
Created on Sep 10, 2016
Last Updated Sep 20, 2016

'''
from datetime import datetime
from time import strftime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.template import RequestContext
from django.utils import timezone
from django.utils.timezone import make_aware, make_naive

from Badges.models import CourseConfigParams
from Instructors.models import (Announcements, Challenges, Courses,
                                InstructorRegisteredCourses, UniversityCourses)
from Instructors.views.utils import current_localtime, datetime_to_local
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def instructorHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        
    # course still not selected
    context_dict['course_Name'] = 'Not Selected'
    context_dict["is_teacher"] = True
        
    course_ID = []      
    course_Name = []        
    course_university = []
    course_end_date_list = []
    announcement_ID = []       
    announcement_course = []         
    start_timestamp = []
    subject = []
    message = []
    
    num_announcements = 0
    
    chall_ID = []
    chall_course = []      
    chall_Name = []         
    start_Timestamp = []
    due_date = []
      
    num_challenges = 0
    currentTime = current_localtime()
    # get only the courses of the logged in user        
    reg_crs = InstructorRegisteredCourses.objects.filter(instructorID=request.user)
    
    for item in reg_crs:
        course_ID.append(item.courseID.courseID) 
        course_Name.append(item.courseID.courseName)
        course_announcements = Announcements.objects.filter(courseID=item.courseID).order_by('-startTimestamp')
        course_challenges = Challenges.objects.filter(courseID=item.courseID, isGraded=True).order_by('dueDate')

        ccp = CourseConfigParams.objects.get(courseID = item.courseID.courseID)
        courseEndDate = ccp.courseEndDate
        course_end_date_list.append(ccp.courseEndDate)

        #get university tied to course to display
        course = item.courseID
        try:
            course_uni = UniversityCourses.objects.get(courseID=course)
        except:
            course_uni = None
        #check in case course was created before requiring university was implemented
        if course_uni is not None:
            course_university.append(course_uni.universityID.universityName)
        else:
            course_university.append("No University Found")
        
        

        if not course_announcements.count()==0:
            last_course_announc= course_announcements[0]
            #if our current time is smaller than the course expiry date, we want to add the announcements
            if not ccp.hasCourseEndDate or currentTime.date() < courseEndDate:
                
                announcement_ID.append(last_course_announc.announcementID)       
                announcement_course.append(item.courseID.courseName)         
                start_timestamp.append(last_course_announc.startTimestamp)
                subject.append(last_course_announc.subject[:25])
                message.append(last_course_announc.message[:300])
                num_announcements = num_announcements+1
        if not course_challenges.count() == 0:
            for c in course_challenges:
                if c.isVisible and (not ccp.hasCourseEndDate or currentTime.date() < courseEndDate): # Showing only visible challenges
                    # Check if current time is within the start and end time of the challenge
                    if c.hasStartTimestamp and currentTime > datetime_to_local(c.startTimestamp):
                        if c.hasDueDate and currentTime < datetime_to_local(c.dueDate):
                            chall_ID.append(c.challengeID) #pk
                            chall_course.append(c.courseID.courseName)
                            chall_Name.append(c.challengeName)
                            start_Timestamp.append(c.startTimestamp)
                            due_date.append(c.dueDate)
                            num_challenges = num_challenges+1
                            break
    
    # casefold will ignore cases when sorting alphabetically so ('c' becomes before 'T')
    context_dict['course_range'] = sorted(list(zip(range(1,reg_crs.count()+1),course_ID,course_Name,course_university,course_end_date_list)), key=lambda x: x[2].casefold())
    print(context_dict['course_range'])
    print(course_university)
    context_dict['num_announcements'] = num_announcements
    context_dict['num_challenges'] = num_challenges
    context_dict['announcement_range'] = zip(range(1,num_announcements+1),announcement_ID,announcement_course,start_timestamp,subject,message)
    context_dict['challenge_range'] = zip(range(1,num_challenges+1), chall_ID, chall_course, chall_Name, start_Timestamp, due_date)
    return render(request,'Instructors/InstructorHome.html', context_dict)
