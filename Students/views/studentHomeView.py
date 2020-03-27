'''
Created on Sep 20, 2016

'''
from django.shortcuts import render
from Instructors.models import Announcements, Challenges
from Instructors.constants import anonymous_avatar, default_time_str
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

    chall_ID = []
    chall_course = []      
    chall_Name = []         
    start_Timestamp = []
    due_date = []
    num_challenges = 0

    # get only the courses of the logged in user
    student = Student.objects.get(user=request.user) 
    context_dict['student'] = student
    context_dict['is_test_student'] = student.isTestStudent
    context_dict['is_student'] = True
    if student.isTestStudent:
        context_dict["username"]="Test Student"
    reg_crs = StudentRegisteredCourses.objects.filter(studentID=student)

    #get today's date
    today = datetime.now(tz=timezone.utc).date()
    currentTime = timezone.now()
    for item in reg_crs:
        course = CourseConfigParams.objects.get(courseID=item.courseID.courseID)
        if course.courseStartDate <= today and course.courseEndDate >=today:
            course_ID.append(item.courseID.courseID) 
            course_Name.append(item.courseID.courseName)
            course_available.append(course.courseAvailable)
            course_announcements = Announcements.objects.filter(courseID=item.courseID).order_by('-startTimestamp')
            course_challenges = Challenges.objects.filter(courseID=item.courseID, isGraded=True).order_by('dueDate')

            if not course_announcements.count()==0 and course.courseAvailable:   
                last_course_announc= course_announcements[0]
                announcement_ID.append(last_course_announc.announcementID)       
                announcement_course.append(item.courseID.courseName)         
                start_timestamp.append(last_course_announc.startTimestamp)
                subject.append(last_course_announc.subject[:25])
                message.append(last_course_announc.message[:300])
                num_announcements = num_announcements+1
            # Show upcoming challenges (only one for each course)
            if course_challenges.count() > 0:
                for c in course_challenges:
                    if c.isVisible and today < course.courseEndDate: # Showing only visible challenges
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
                        
                    
    context_dict['course_range'] = sorted(list(zip(range(1,reg_crs.count()+1),course_ID,course_Name, course_available)), key=lambda tup: (-tup[3], tup[2].casefold()))
    context_dict['num_announcements'] = num_announcements
    context_dict['announcement_range'] = zip(range(1,num_announcements+1),announcement_ID,announcement_course,start_timestamp,subject,message)
    context_dict['challenge_range'] = zip(range(1,num_challenges+1), chall_ID, chall_course, chall_Name, start_Timestamp, due_date)
    return render(request,'Students/StudentHome.html', context_dict)