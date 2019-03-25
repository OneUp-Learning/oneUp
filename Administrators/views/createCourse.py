from django.template import RequestContext
from django.shortcuts import render, redirect

from Instructors.models import Courses, Instructors, InstructorRegisteredCourses, Challenges, Topics, CoursesTopics, ActivitiesCategory
from Instructors.constants import uncategorized_activity
from Badges.models import CourseConfigParams

from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime

from Instructors.constants import unassigned_problems_challenge_name, unspecified_topic_name, default_time_str, anonymous_avatar
from Instructors.views.utils import utcDate
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from django.contrib.auth.models import User
from oneUp.decorators import adminsCheck
from oneUp.ckeditorUtil import config_ck_editor

def add_instructor_test_student(instructor,course):
    # Add test student to the course while adding instructor to the course
    # Note: Some of the conditions codes try to handle exceptions for instructors with no test_student accounts, once every instructor has an associated test student account , some codes can be removed
    student = Student.objects.filter(user = instructor)
    if student:
        student = student[0]
        newStudent = False
    else:
        # Otherwise test student is not created yet, create test student, register student to the course and configure course params
        student = Student()
        student.user = instructor
        student.universityID = instructor.email
        student.isTestStudent = True
        student.save()
        newStudent = True
    
    if newStudent:
        studentRegisteredCourse = StudentRegisteredCourses()
    else:
        studentRegisteredCourses = StudentRegisteredCourses.objects.filter(courseID=course)
        if studentRegisteredCourses:
            studentRegisteredCourse = studentRegisteredCourses[0]
        else:
             # Add test student to the course while adding instructor to the course
            studentRegisteredCourse = StudentRegisteredCourses()
        
    studentRegisteredCourse.studentID = student
    studentRegisteredCourse.courseID = course
    studentRegisteredCourse.avatarImage = anonymous_avatar
    studentRegisteredCourse.save()

    if newStudent:
        scparams = StudentConfigParams()
    else:      
        # Configure params for test student
        scparamsList = StudentConfigParams.objects.filter(courseID=course)
        if scparamsList:
            scparams = scparamsList[0]
        else:
            scparams = StudentConfigParams()
    scparams.courseID = course
    scparams.studentID = student
    scparams.save()



@login_required
@user_passes_test(adminsCheck,login_url='/oneUp/home',redirect_field_name='')
def courseCreateView(request):
    
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
    context_dict["username"]=user.username
                
    if request.method == 'POST':
        name = request.POST['courseName']
        description = request.POST['courseDescription']
        if 'instructorName' in request.POST:
            instructor_username = request.POST['instructorName']
        
        if 'courseID' in request.GET: # Editing course
            courses = Courses.objects.filter(courseName = name)
            if name == request.POST['cNamePrev']: # if the course name has not change when editing
                course = courses[0]
                course.courseDescription = description
                course.save()
                if 'instructorName' in request.POST:
                    instructor = User.objects.get(username=instructor_username)
                    irc = InstructorRegisteredCourses.objects.filter(courseID = course)
                    if irc.exists():
                        irc = irc.first()
                        irc.instructorID = instructor
                        irc.save()
                                                    
                    else:
                        irc = InstructorRegisteredCourses()
                        irc.instructorID = instructor
                        irc.courseID = course
                        irc.save()

                    add_instructor_test_student(instructor,course)
                
                ccp = CourseConfigParams.objects.get(courseID = course)
                if('courseStartDate' in request.POST and request.POST['courseStartDate'] == ""):
                    ccp.courseStartDate = utcDate()
                else:
                    ccp.courseStartDate = utcDate(request.POST['courseStartDate'], "%B %d, %Y")
        
                if('courseEndDate' in request.POST and request.POST['courseEndDate'] == ""):
                    ccp.courseEndDate = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
                else:
                     ccp.courseEndDate = utcDate(request.POST['courseEndDate'], "%B %d, %Y")
                
                ccp.save()
            elif courses: # The new course name is already chosen
                context_dict['errorMessage'] = "Course name taken."
            else: # The new course name is not chosen so change it
                course = Courses.objects.get(courseName = request.POST['cNamePrev'])
                course.courseName = name
                course.courseDescription = description
                course.save()
                
                if 'instructorName' in request.POST:
                    instructor = User.objects.get(username=instructor_username)
                    irc = InstructorRegisteredCourses.objects.filter(courseID = course)
                    if irc.exists():
                        irc = irc.first()
                        irc.instructorID = instructor
                        irc.save()
                        
                    else:
                        irc = InstructorRegisteredCourses()
                        irc.instructorID = instructor
                        irc.courseID = course
                        irc.save()
                        
                    add_instructor_test_student(instructor,course)
        
                ccp = CourseConfigParams.objects.get(courseID = course)
                if('courseStartDate' in request.POST and request.POST['courseStartDate'] == ""):
                    ccp.courseStartDate = utcDate()
                else:
                    ccp.courseStartDate = utcDate(request.POST['courseStartDate'], "%B %d, %Y")
        
                if('courseEndDate' in request.POST and request.POST['courseEndDate'] == ""):
                    ccp.courseEndDate = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
                else:
                     ccp.courseEndDate = utcDate(request.POST['courseEndDate'], "%B %d, %Y")
                
                ccp.save()
                
        else: # Creating a new course
            courseExist = Courses.objects.filter(courseName = name)
            if courseExist:
                context_dict['errorMessage'] = "Course name taken."
            else:
                course = Courses()
                course.courseName = name
                course.courseDescription = description
                course.save()
                
                if 'instructorName' in request.POST:
                    instructor = User.objects.get(username=instructor_username)
                    
                    irc = InstructorRegisteredCourses()
                    irc.instructorID = instructor
                    irc.courseID = course
                    irc.save()
                    
                    add_instructor_test_student(instructor,course)
                    
                ccp = CourseConfigParams()
                ccp.courseID = course
                if('courseStartDate' in request.POST and request.POST['courseStartDate'] == ""):
                    ccp.courseStartDate = utcDate()
                else:
                    ccp.courseStartDate = utcDate(request.POST['courseStartDate'], "%B %d, %Y")
        
                if('courseEndDate' in request.POST and request.POST['courseEndDate'] == ""):
                    ccp.courseEndDate = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
                else:
                     ccp.courseEndDate = utcDate(request.POST['courseEndDate'], "%B %d, %Y")
                     
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
                defaultActivityCategory.courseID = course
                defaultActivityCategory.save()
            
            
    # Add users who are instructors to the instructors list (AH)
    context_dict['instructors'] = User.objects.filter(groups__name="Teachers")
    
    # Get all courses (AH)
    courses = Courses.objects.all()
    course_ID = []
    course_Name = []
    for c in courses:
        course_ID.append(c.courseID)
        course_Name.append(c.courseName)

    context_dict['courses'] = zip(range(1, len(courses)+1), course_ID, course_Name)
    if 'courseID' in request.GET:
        course = Courses.objects.get(courseID = request.GET['courseID'])
        context_dict['courseName'] = course.courseName
        context_dict['courseDescription'] = course.courseDescription
        irc = InstructorRegisteredCourses.objects.filter(courseID = request.GET['courseID'])
        if irc.exists():
            context_dict['instructorName'] = irc.first().instructorID.username
        ccparams = CourseConfigParams.objects.get(courseID = request.GET['courseID'])
        defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        if(ccparams.courseStartDate.year < defaultTime.year):
            context_dict["courseStartDate"]=ccparams.courseStartDate.strftime("%B %d, %Y")
        else:
            context_dict["courseStartDate"]=""
        if(ccparams.courseEndDate.year < defaultTime.year):
            context_dict["courseEndDate"]=ccparams.courseEndDate.strftime("%B %d, %Y")
        else:
            context_dict["courseEndDate"]=""
        context_dict['editCourse'] = True
    context_dict['view'] = False
    context_dict['ckeditor'] = config_ck_editor()
        
    return render(request,'Administrators/createCourse.html',context_dict)
            