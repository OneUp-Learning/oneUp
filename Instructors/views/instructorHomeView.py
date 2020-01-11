'''
Created on Sep 10, 2016
Last Updated Sep 20, 2016

'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Courses, InstructorRegisteredCourses, Announcements, Challenges
from time import strftime
from datetime import datetime
from Badges.models import CourseConfigParams
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck    
from django.utils import timezone 
from django.utils.timezone import make_naive, make_aware
from Instructors.constants import default_time_str

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
    currentTime = timezone.now()
    # get only the courses of the logged in user        
    reg_crs = InstructorRegisteredCourses.objects.filter(instructorID=request.user)
    
    for item in reg_crs:
        course_ID.append(item.courseID.courseID) 
        course_Name.append(item.courseID.courseName)
        course_announcements = Announcements.objects.filter(courseID=item.courseID).order_by('-startTimestamp')
        course_challenges = Challenges.objects.filter(courseID=item.courseID, isGraded=True).order_by('dueDate')

        ccp = CourseConfigParams.objects.get(courseID = item.courseID.courseID)
        courseEndDate= make_aware(datetime.combine(ccp.courseEndDate, datetime.min.time()))
        
        if not course_announcements.count()==0:
            last_course_announc= course_announcements[0]
            #if our current time is smaller than the course expiry date, we want to add the announcements
            if currentTime < courseEndDate:
                
                announcement_ID.append(last_course_announc.announcementID)       
                announcement_course.append(item.courseID.courseName)         
                start_timestamp.append(last_course_announc.startTimestamp)
                subject.append(last_course_announc.subject[:25])
                message.append(last_course_announc.message[:300])
                num_announcements = num_announcements+1
        if not course_challenges.count() == 0:
                for c in course_challenges:
                    if c.isVisible and currentTime < courseEndDate: # Showing only visible challenges
                        # Check if current time is within the start and end time of the challenge
                        if currentTime > c.startTimestamp:
                            if currentTime < c.dueDate and not datetime.strptime(str(c.dueDate.replace(microsecond=0)), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p") == default_time_str:
                                chall_ID.append(c.challengeID) #pk
                                chall_course.append(c.courseID.courseName)
                                chall_Name.append(c.challengeName)
                                start_Timestamp.append(c.startTimestamp)
                                due_date.append(c.dueDate)
                                num_challenges = num_challenges+1
                                break
                        
    # casefold will ignore cases when sorting alphabetically so ('c' becomes before 'T')
    context_dict['course_range'] = sorted(list(zip(range(1,reg_crs.count()+1),course_ID,course_Name)), key=lambda x: x[2].casefold())
    print(context_dict['course_range'])
    context_dict['num_announcements'] = num_announcements
    context_dict['num_challenges'] = num_challenges
    context_dict['announcement_range'] = zip(range(1,num_announcements+1),announcement_ID,announcement_course,start_timestamp,subject,message)
    context_dict['challenge_range'] = zip(range(1,num_challenges+1), chall_ID, chall_course, chall_Name, start_Timestamp, due_date)
    return render(request,'Instructors/InstructorHome.html', context_dict)
