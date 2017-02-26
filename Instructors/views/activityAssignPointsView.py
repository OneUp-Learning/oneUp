#
# Created on  11/20/2015
# Dillon Perry, Austin Hodge
#
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Students.models import StudentRegisteredCourses, Student
from Instructors.models import Courses, Activities
from Students.models import StudentActivities
from Badges.events import register_event
from Badges.enums import Event
from Instructors.views.activityListView import createContextForActivityList

def activityAssignPointsView(request):   
    
    if request.method == 'POST':
        # Get all students assigned to the current course (AH)
        studentList = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
        for student in studentList:
            # See if a student is graded for this activity (AH)
            # Should only be one match (AH)
            assignment = StudentActivities.objects.filter(activityID = request.POST['activityID'], studentID = student.studentID.id).first()
            studentPoints = request.POST['student_Points' + str(student.studentID.id)] 
                       
            # If student has been previously graded...
            if assignment:
                # Check if the student has points wanting to be assigned (AH)
                if not studentPoints == '0':
                    # Override the activity with the student points (AH)
                    assignment.activityScore = studentPoints
                    assignment.instructorFeedback =  request.POST['student_Feedback' + str(student.studentID.id)]
                    assignment.timestamp = datetime.now()
                    assignment.save()

                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignment.studentID, assignment.activityID.activityID)
                    print("Registered Event: Participation Noted Event, Student: " + str(assignment.studentID) + ", Activity Assignment: " + str(assignment.studentActivityAssignmentID))
                else:
                    # Delete activity assignment if student points is empty = 0 (AH)
                    assignment.delete()       
            else:
                # Create new assigned activity object for the student if there are points entered to be assigned (AH)
                if not studentPoints == '0':
                    # Create new activity (AH)
                    assignment = StudentActivities()
                    assignment.activityID = Activities.objects.get(activityID = request.POST['activityID'])
                    assignment.studentID = Student.objects.get(pk = student.studentID.id)
                    assignment.activityScore = studentPoints
                    assignment.timestamp = datetime.now()
                    assignment.instructorFeedback =  request.POST['student_Feedback' + str(student.studentID.id)]
                    assignment.save()

                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignment.studentID, assignment.activityID.activityID)
       
                    print("Registered Event: Participation Noted Event, Student: " + str(assignment.studentID) + ", Activity Assignment: " + str(assignment.studentActivityAssignmentID))                           
    
    # prepare context for Activity List      
    context_dict = createContextForActivityList(request) 

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    return redirect('/oneUp/instructors/activitiesList', context_dict)    
        
        
def createContextForPointsAssignment(request):
    context_dict = { }
    student_ID = []
    student_Name = []
    student_Points = []    
    student_Feedback = []
    
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
    
    for stud_course in studentCourse:
        student = stud_course.studentID
        student_ID.append(student.id)
        student_Name.append((student).user.get_full_name())
        if (StudentActivities.objects.filter(activityID = request.GET['activityID'], studentID = student)).exists():
            stud_act = StudentActivities.objects.get(activityID = request.GET['activityID'], studentID = student)
            student_Points.append(stud_act.activityScore)
            student_Feedback.append(stud_act.instructorFeedback)
        else:
            student_Points.append("0")
            student_Feedback.append("")
        
    context_dict['activityID'] = request.GET['activityID']
    context_dict['activityName'] = Activities.objects.get(activityID = request.GET['activityID']).activityName
    context_dict['assignedActivityPoints_range'] = zip(range(1,len(student_ID)+1),student_ID,student_Name,student_Points, student_Feedback)
    return context_dict
    
@login_required
def assignedPointsList(request):

    context_dict = createContextForPointsAssignment(request)

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'        

    return render(request,'Instructors/ActivityAssignPointsForm.html', context_dict)

        