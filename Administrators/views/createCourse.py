from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.utils import timezone

from Badges.models import CourseConfigParams, VirtualCurrencyCustomRuleInfo
from Instructors.constants import (anonymous_avatar,
                                   unassigned_problems_challenge_name,
                                   uncategorized_activity,
                                   unspecified_topic_name,
                                   unspecified_vc_manual_rule_description,
                                   unspecified_vc_manual_rule_name)
from Instructors.models import (ActivitiesCategory, Challenges, Courses,
                                CoursesTopics, FlashCardGroup,
                                FlashCardGroupCourse,
                                InstructorRegisteredCourses, Instructors,
                                Topics, Universities, UniversityCourses,InstructorToUniversities)
from Instructors.views.utils import date_to_selected, str_datetime_to_local
from oneUp.ckeditorUtil import config_ck_editor
from oneUp.decorators import adminsCheck
from Students.models import (Student, StudentConfigParams,
                             StudentRegisteredCourses)
from Instructors.views.preferencesView import createSCVforInstructorGrant
import json



def add_instructor_test_student(instructor, course):
    # Add test student to the course while adding instructor to the course
    # Note: Some of the conditions codes try to handle exceptions for instructors with no test_student accounts, once every instructor has an associated test student account , some codes can be removed
    student = Student.objects.filter(user=instructor)
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
        studentRegisteredCourses = StudentRegisteredCourses.objects.filter(
            courseID=course, studentID=student)
        if studentRegisteredCourses:
            studentRegisteredCourse = studentRegisteredCourses[0]
        else:
             # Add test student to the course while adding instructor to the course
            studentRegisteredCourse = StudentRegisteredCourses()

    studentRegisteredCourse.studentID = student
    studentRegisteredCourse.courseID = course
    studentRegisteredCourse.avatarImage = anonymous_avatar
    if CourseConfigParams.objects.filter(courseID = course).exists():
        ccparams = CourseConfigParams.objects.get(courseID = course)
        if ccparams.virtualCurrencyAdded:
            # We have now switched to the canonical virtual currency amount a student has being determined by their transactions,
            # so we first add a StudentVirtualCurrency entry to show their gain and then we adjust the virtualCurrencyAmount.
            createSCVforInstructorGrant(student,course,ccparams.virtualCurrencyAdded)
            studentRegisteredCourse.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
    studentRegisteredCourse.save()

    if newStudent:
        scparams = StudentConfigParams()
    else:
        # Configure params for test student
        scparamsList = StudentConfigParams.objects.filter(
            courseID=course, studentID=student)
        if scparamsList:
            scparams = scparamsList[0]
        else:
            scparams = StudentConfigParams()
    scparams.courseID = course
    scparams.studentID = student
    scparams.save()


def remove_test_student(instructor, course):
    # Removes the test student from the course along with their config
    # when a instructor is removed from a course
    # Does not remove the actual Student object (AH)
    student = Student.objects.filter(user=instructor)
    if not student.exists():
        return
    student = student[0]

    studentRegisteredCourses = StudentRegisteredCourses.objects.filter(
        courseID=course, studentID=student)
    if studentRegisteredCourses.exists():
        for registered_courses in studentRegisteredCourses:
            registered_courses.delete()

    scparamsList = StudentConfigParams.objects.filter(
        courseID=course, studentID=student)
    if scparamsList.exists():
        for scparams in scparamsList:
            scparams.delete()


@login_required
@user_passes_test(adminsCheck, login_url='/oneUp/home', redirect_field_name='')
def courseCreateView(request):

    context_dict = {}
    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
    context_dict["username"] = user.username

    if request.method == 'POST':
        
        name = request.POST['courseName']
        description = request.POST['courseDescription']
        university_name = request.POST['universityName']
        university = Universities.objects.filter(universityName=university_name).first()
        instructors = []
        if 'instructorName' in request.POST:
            instructor_usernames = request.POST.getlist('instructorName')
            instructors = [User.objects.get(
                username=instructor_username) for instructor_username in instructor_usernames]

        if 'courseID' in request.GET:  # Editing course
            courses = Courses.objects.filter(courseName=name)
            
            # if the course name has not change when editing
            if name == request.POST['cNamePrev']:
                course = courses[0]
                course.courseDescription = description
                course.save()
                uC = UniversityCourses.objects.filter(courseID = course).first()
                #in case editing a course created before university requirement
                if uC is not None:
                    uC = UniversityCourses.objects.filter(courseID = course).first()
                    uC.universityID = university
                    uC.save()
                else:
                    uC = UniversityCourses()
                    uC.universityID = university
                    uC.courseID = course
                    uC.save()
                instructors_to_remove = InstructorRegisteredCourses.objects.filter(
                    courseID=course).exclude(instructorID__in=instructors)

                if 'instructorName' in request.POST:
                    irc = InstructorRegisteredCourses.objects.filter(
                        courseID=course, instructorID__in=instructors)

                    # Register instructors to the course (AH)
                    for instructor in instructors:
                        # If this instructor is registered for course then skip
                        if InstructorRegisteredCourses.objects.filter(instructorID=instructor, courseID=course).exists():
                            continue
                        else:
                            irc = InstructorRegisteredCourses()
                            irc.instructorID = instructor
                            irc.courseID = course
                            irc.save()

                        add_instructor_test_student(instructor, course)

                # Remove instructors that were not selected from the course
                if instructors_to_remove.exists():
                    print(instructors_to_remove)
                    for registered_courses in instructors_to_remove:
                        remove_test_student(
                            registered_courses.instructorID, course)
                        registered_courses.delete()

                ccp = CourseConfigParams.objects.get(courseID=course)
                if 'courseStartDate' in request.POST and request.POST['courseStartDate'] != "":
                    ccp.courseStartDate = str_datetime_to_local(request.POST['courseStartDate'], to_format="%B %d, %Y") 
                    ccp.hasCourseStartDate = True
                else:
                    ccp.hasCourseStartDate = False

                if 'courseEndDate' in request.POST and request.POST['courseEndDate'] != "":
                    ccp.courseEndDate = str_datetime_to_local(request.POST['courseEndDate'], to_format="%B %d, %Y")
                    ccp.hasCourseEndDate = True
                else:
                    ccp.hasCourseEndDate = False

                ccp.save()
            elif courses:  # The new course name is already chosen
                context_dict['errorMessage'] = "Course name taken."
            else:  # The new course name is different from old one and is unique so change it
                course = Courses.objects.get(
                    courseName=request.POST['cNamePrev'])
                course.courseName = name
                course.courseDescription = description
                course.save()
                uC = UniversityCourses.objects.filter(courseID = course).first()
                uC.universityID = university
                uC.save()

                if 'instructorName' in request.POST:
                    irc = InstructorRegisteredCourses.objects.filter(
                        courseID=course, instructorID__in=instructors)
                    instructors_to_remove = InstructorRegisteredCourses.objects.filter(
                        courseID=course).exclude(instructorID__in=instructors)
                    # Register instructors to the course
                    for instructor in instructors:
                        # If this instructor is registered for course then skip
                        if irc.filter(instructorID=instructor).exists():
                            continue
                        else:
                            irc = InstructorRegisteredCourses()
                            irc.instructorID = instructor
                            irc.courseID = course
                            irc.save()

                        add_instructor_test_student(instructor, course)

                    # Remove instructors that were not selected from the course
                    if instructors_to_remove.exists():
                        for registered_courses in instructors_to_remove:
                            remove_test_student(
                                registered_courses.instructorID, course)
                            registered_courses.delete()

                ccp = CourseConfigParams.objects.get(courseID=course)
                if 'courseStartDate' in request.POST and request.POST['courseStartDate'] != "":
                    ccp.courseStartDate = str_datetime_to_local(request.POST['courseStartDate'], to_format="%B %d, %Y") 
                    ccp.hasCourseStartDate = True
                else:
                    ccp.hasCourseStartDate = False

                if 'courseEndDate' in request.POST and request.POST['courseEndDate'] != "":
                    ccp.courseEndDate = str_datetime_to_local(request.POST['courseEndDate'], to_format="%B %d, %Y")
                    ccp.hasCourseEndDate = True
                else:
                    ccp.hasCourseEndDate = False

                ccp.save()

        else:  # Creating a new course
            courseExist = Courses.objects.filter(courseName=name)
            if courseExist:
                context_dict['errorMessage'] = "Course name taken."
            else:
                course = Courses()
                course.courseName = name
                course.courseDescription = description
                course.save()

                
                if not UniversityCourses.objects.filter(courseID=course):
                    uC = UniversityCourses()
                    uC.universityID = university
                    uC.courseID = course
                    uC.save()
                if 'instructorName' in request.POST:
                    for instructor in instructors:

                        irc = InstructorRegisteredCourses()
                        irc.instructorID = instructor
                        irc.courseID = course
                        irc.save()

                        add_instructor_test_student(instructor, course)

                ccp = CourseConfigParams()
                ccp.courseID = course
                if 'courseStartDate' in request.POST and request.POST['courseStartDate'] != "":
                    ccp.courseStartDate = str_datetime_to_local(request.POST['courseStartDate'], to_format="%B %d, %Y")

                    ccp.hasCourseStartDate = True

                if 'courseEndDate' in request.POST and request.POST['courseEndDate'] != "":
                    ccp.courseEndDate = str_datetime_to_local(request.POST['courseEndDate'], to_format="%B %d, %Y")
                    ccp.hasCourseEndDate = True

                ccp.save()

                # Add a default unassigned problem for this course
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

                #Add default unassigned group for flash cards
                unassigned_flashgroup = FlashCardGroup()
                unassigned_flashgroup.groupName = "Unassigned"
                unassigned_flashgroup.save()

                course_group = FlashCardGroupCourse()
                course_group.groupID = unassigned_flashgroup
                course_group.courseID= course
                course_group.save()

                # Add a default category
                defaultActivityCategory = ActivitiesCategory()
                defaultActivityCategory.name = uncategorized_activity
                defaultActivityCategory.courseID = course
                defaultActivityCategory.save()

                # Add a default manual earning VC rule
                manual_earning_rule = VirtualCurrencyCustomRuleInfo()
                manual_earning_rule.courseID = course
                manual_earning_rule.vcRuleName = unspecified_vc_manual_rule_name
                manual_earning_rule.vcRuleType = True
                manual_earning_rule.vcRuleDescription = unspecified_vc_manual_rule_description
                manual_earning_rule.vcRuleAmount = -1
                manual_earning_rule.vcAmountVaries = True
                manual_earning_rule.save()

    # Add users who are instructors to the instructors list (AH)
    context_dict['instructors'] = User.objects.filter(groups__name="Teachers")
    
    # Get all courses (AH)
    courses = Courses.objects.all()
    course_ID = []
    course_Name = []
    for c in courses:
        course_ID.append(c.courseID)
        course_Name.append(c.courseName)

    context_dict['courses'] = zip(
        range(1, len(courses)+1), course_ID, course_Name)
    #get universities to display in select form
    universities = Universities.objects.all()
    universities_names = []
    for uni in universities:
        universities_names.append(uni.universityName)

    context_dict['universities'] = sorted(universities_names)
    
    if 'courseID' in request.GET:
        course = Courses.objects.get(courseID=request.GET['courseID'])
        context_dict['cid']=request.GET['courseID']
        
        context_dict['courseName'] = course.courseName
        context_dict['courseDescription'] = course.courseDescription
        try:
            context_dict['universityNames'] = UniversityCourses.objects.filter(courseID=course).first().universityID.universityName
        except:
            context_dict['universityNames'] = ""
        uni_instructors, retrieved_instructors = retrieveInstructors(context_dict['universityNames'], course)
        context_dict['uniInstructors'] = json.dumps(uni_instructors)
        context_dict['retrievedInstructors'] = json.dumps(retrieved_instructors)

        irc = InstructorRegisteredCourses.objects.filter(
            courseID=request.GET['courseID'])

        if irc.exists():
            context_dict['instructorNames'] = [
                instructor.instructorID.username for instructor in irc]

        ccparams = CourseConfigParams.objects.get(
            courseID=request.GET['courseID'])

        
        if ccparams.hasCourseStartDate:
            context_dict["courseStartDate"] = date_to_selected(ccparams.courseStartDate, to_format="%B %d, %Y")
        else:
            context_dict["courseStartDate"] = ""

        if ccparams.hasCourseEndDate:
            context_dict["courseEndDate"] = date_to_selected(ccparams.courseEndDate, to_format="%B %d, %Y")
        else:
            context_dict["courseEndDate"] = ""

        context_dict['editCourse'] = True


    context_dict['view'] = False
    context_dict['ckeditor'] = config_ck_editor()

    return render(request, 'Administrators/createCourse.html', context_dict)
#triggered by ajax function when user selects a university in the form
def retrieveInstructorsAjax(request):
    
    university_name = request.POST['name']
    
    if 'courseID' in request.GET:
        course = Courses.objects.get(courseID=request.GET['courseID'])
        uni_instructors, instructors = retrieveInstructors(university_name,course)
    else:
        uni_instructors, instructors = retrieveInstructors(university_name)
    return JsonResponse({"uniInstructors" : uni_instructors, "instructors":instructors})

#get the appropriatly sorted list of instructors, prioritized dynamically by the university selected
def retrieveInstructors(university_name, course = None):
    
    university = Universities.objects.filter(universityName=university_name).first()
    university_instructors_list = []
    instructors_list = []
    instructors = InstructorToUniversities.objects.filter(universityID=university)
    course_instructors = None
    
    if course:
        course_instructors = InstructorRegisteredCourses.objects.filter(courseID=course).values_list('instructorID__username', flat=True)
    


    for instructor in instructors:
        selected = False
        if course_instructors:
            selected = instructor.instructorID.username in course_instructors
        university_instructors_list.append({"name":instructor.instructorID.username, "selected":selected})
    other_instructors = User.objects.filter(groups__name="Teachers").exclude(username__in = [x["name"] for x in university_instructors_list])
    
    for instructor in other_instructors:
        selected = False
        if course_instructors:
            selected = instructor.username in course_instructors
        instructors_list.append({"name":instructor.username, "selected":selected})
    return sorted(university_instructors_list, key = lambda i : i['name']), sorted(instructors_list, key = lambda i : i['name'])
