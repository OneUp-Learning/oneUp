#
# Created on  11/20/2015
# Dillon Perry
#
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Students.models import StudentRegisteredCourses, Student
from Instructors.models import Courses, Activities
from Instructors.models import AssignedActivities
from Badges.events import register_event
from Badges.enums import Event
from Instructors.views.activityListView import createContextForActivityList

def activityAssignPointsView(request):
    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['studentName','activityName', 'points'];
    
    
    if request.method == 'POST':
        # Get all students assigned to the current course (AH)
        studentList = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
        for student in studentList:
            # See if a student is assigned to this activity (AH)
            # Should only be one match (AH)
            assignments = AssignedActivities.objects.filter(activityID = request.POST['activityID'], recipientStudentID = student.studentID.id).first()
            studentPoints = request.POST[str(student.studentID.id)]
            #print("Student Points: " + studentPoints)
            
            # If student is assigned to this activity...
            if assignments:
                # Check if the student has points wanting to be assigned (AH)
                if not studentPoints == '0':
                    # Override the activity with the student points (AH)
                    assignments.pointsReceived = request.POST[str(student.studentID.id)]
                    assignments.save()
                    #print("Override")
                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignments.recipientStudentID, assignments.activityID.activityID)
                    print("Registered Event: Participation Noted Event, Student: " + str(assignments.recipientStudentID) + ", Activity Assignment: " + str(assignments.activityAssigmentID))
                else:
                    # Delete activity assignment if student points is empty = 0 (AH)
                    assignments.delete()       
                    #print("Deleted")
            else:
                # Create new assigned activity object for the student if it has points wanting to be assigned (AH)
                if not studentPoints == '0':
                    # Create new activity (AH)
                    assignment = AssignedActivities()
                    assignment.activityID = Activities.objects.get(activityID = request.POST['activityID'])
                    assignment.recipientStudentID = Student.objects.get(pk = student.studentID.id)
                    assignment.pointsReceived = request.POST[str(student.studentID.id)]
                    assignment.save()
                    #print("New")
                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignment.recipientStudentID, assignment.activityID.activityID)
       
                    print("Registered Event: Participation Noted Event, Student: " + str(assignment.recipientStudentID) + ", Activity Assignment: " + str(assignment.activityAssigmentID))                           
    
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
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
    
    for student in studentCourse:
        student_ID.append(student.studentID.id)
        student_Name.append((student.studentID).user.get_full_name())
        if AssignedActivities.objects.filter(activityID = request.GET['activityID'], recipientStudentID = student.studentID.id).exists():
            student_Points.append(AssignedActivities.objects.get(activityID = request.GET['activityID'], recipientStudentID = student.studentID.id).pointsReceived)
        else:
            student_Points.append("0")
        
    context_dict['activityID'] = request.GET['activityID']
    context_dict['activityName'] = Activities.objects.get(activityID = request.GET['activityID']).activityName
    context_dict['assignedActivityPoints_range'] = zip(range(1,len(student_ID)+1),student_ID,student_Name,student_Points)
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

        