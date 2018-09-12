'''
Created on Sep 10, 2016
Last Updated Sep 20, 2016

'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Courses, InstructorRegisteredCourses, Announcements, Challenges
from time import strftime
from django.contrib.auth.decorators import login_required

@login_required

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
    end_Timestamp = []
      
    num_challenges = 0
    currentTime = strftime("%Y-%m-%d %H:%M:%S")
    # get only the courses of the logged in user        
    reg_crs = InstructorRegisteredCourses.objects.filter(instructorID=request.user)
    for item in reg_crs:
        course_ID.append(item.courseID.courseID) 
        course_Name.append(item.courseID.courseName)
        course_announcements = Announcements.objects.filter(courseID=item.courseID).order_by('-startTimestamp')
        course_challenges = Challenges.objects.filter(courseID=item.courseID, isGraded=True).order_by('endTimestamp')
        if not course_announcements.count()==0:    
            last_course_announc= course_announcements[0]
            announcement_ID.append(last_course_announc.announcementID)       
            announcement_course.append(item.courseID.courseName)         
            start_timestamp.append(last_course_announc.startTimestamp)
            subject.append(last_course_announc.subject[:25])
            message.append(last_course_announc.message[:300])
            num_announcements = num_announcements+1
        if not course_challenges.count() == 0:
            for c in course_challenges:
                if c.isVisible: # Showing only visible challenges
                    # Check if current time is within the start and end time of the challenge
                    if currentTime > c.startTimestamp.strftime("%Y-%m-%d %H:%M:%S"):
                        if currentTime < c.endTimestamp.strftime("%Y-%m-%d %H:%M:%S"):
                            chall_ID.append(c.challengeID) #pk
                            chall_course.append(item.courseID.courseName)
                            chall_Name.append(c.challengeName)
                            start_Timestamp.append(c.startTimestamp)
                            end_Timestamp.append(c.endTimestamp)
                            num_challenges = num_challenges+1
                            break
                    
    context_dict['course_range'] = zip(range(1,reg_crs.count()+1),course_ID,course_Name)
    context_dict['num_announcements'] = num_announcements
    context_dict['num_challenges'] = num_challenges
    context_dict['announcement_range'] = zip(range(1,num_announcements+1),announcement_ID,announcement_course,start_timestamp,subject,message)
    context_dict['challenge_range'] = zip(range(1,num_challenges+1), chall_ID, chall_course, chall_Name, start_Timestamp, end_Timestamp)
    return render(request,'Instructors/InstructorHome.html', context_dict)
