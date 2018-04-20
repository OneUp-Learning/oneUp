from django.template import RequestContext
from django.shortcuts import render, redirect

from Instructors.models import Courses, Instructors, InstructorRegisteredCourses, Challenges, Topics, CoursesTopics, ActivitiesCategory
from Instructors.constants import uncategorized_activity
from Badges.models import CourseConfigParams

from django.contrib.auth.decorators import login_required
from datetime import datetime

from Instructors.constants import unassigned_problems_challenge_name, unspecified_topic_name, default_time_str
from Instructors.views.utils import utcDate
from django.contrib.auth.models import User

def courseCreateView(request):
    
        context_dict = { }
        context_dict["logged_in"]=request.user.is_authenticated()
        if request.user.is_authenticated():
            user = request.user
        context_dict["username"]=user.username
                
        # Add users who are instructors to the instructors list (AH)
        instructors = []
        users = User.objects.all()
        for u in users:
             if u.groups.filter(name='Teachers').exists():
                 instructors.append(u)

        context_dict['instructors'] = instructors
        
        # Get all courses (AH)
        courses = Courses.objects.all()
        print("Courses:", courses)
        course_ID = []
        course_Name = []
        for c in courses:
            course_ID.append(c.courseID)
            course_Name.append(c.courseName)
        
        context_dict['courses'] = zip(range(1, len(courses)+1), course_ID, course_Name)
            
        if request.method=='GET':
            return render(request,'Administrators/createCourse.html',context_dict) 
        else: # Method is POST
            name = request.POST['name']
            description = request.POST['description']
            instructor_username = request.POST['instructor_username']
            
            course = Courses()
            course.courseName = name
            course.courseDescription = description
            course.save()
            
            instructor = User.objects.get(username=instructor_username)
            
            irc = InstructorRegisteredCourses()
            irc.instructorID = instructor
            irc.courseID = course
            irc.save()
            
            ccp = CourseConfigParams()
            ccp.courseID = course
            if 'course_start_date' in request.POST and request.POST['course_start_date']:
                if(request.POST['course_start_date'] == ""):
                    ccp.courseStartDate = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
                else:
                    ccp.courseStartDate = utcDate(request.POST['course_start_date'], "%m/%d/%Y %I:%M %p")
                    print(ccp.courseStartDate)

                print(request.POST['course_start_date'])
                #ccp.courseStartDate = datetime(request.POST['course_start_date'])
            if 'course_end_date' in request.POST and request.POST['course_end_date']:
                if(request.POST['course_end_date'] == ""):
                    ccp.courseEndDate = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
                else:
                    ccp.courseEndDate = utcDate(request.POST['course_end_date'], "%m/%d/%Y %I:%M %p")
                    print(ccp.courseEndDate)
                #ccp.courseStartDate = datetime(request.POST['course_end_date'])
            ccp.save()
            
            unassigned_problem_challenge = Challenges()
            unassigned_problem_challenge.challengeName = unassigned_problems_challenge_name
            unassigned_problem_challenge.courseID = course
            unassigned_problem_challenge.numberAttempts = 0
            unassigned_problem_challenge.timeLimit = 0
            unassigned_problem_challenge.save()
            
            # Add a default topic for this course
            topic = Topics()
            topic.topicName = unspecified_topic_name
            topic.save()
            
            courseTopic = CoursesTopics()
            courseTopic.topicID = topic
            courseTopic.courseID = course
            courseTopic.save()
            
            #Add a default category
            defaultActivityCategory = ActivitiesCategory()
            defaultActivityCategory.name = uncategorized_activity
            defaultActivityCategory.categoryID = course
            defaultActivityCategory.save()
            
            
            
            return render(request,'Administrators/createCourse.html',context_dict)
            