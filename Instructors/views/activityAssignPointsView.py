#
# Created on  11/20/2015
# Dillon Perry
#
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Students.models import StudentActivities, Student
from Instructors.models import Courses, Activities
from Instructors.models import AssignedActivities
from Badges.events import register_event
from Badges.enums import Event
from Instructors.views.activityListView import createContextForActivityList

@login_required
def activityAssignPointsView(request):
    #request the context of the request
    #The request contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['studentName','activityName', 'points'];
    
    
    if request.method == 'POST':
        #Assign points to each checked student for completing an activity
        
        if 'studentSelect[]' and 'activity' and 'points' in request.POST:
            studentList = request.POST.getlist('studentSelect[]')
            # Get assigned activities for current activity being submitted (AH)
            # Filter by the name of the activity/ID (AH)
            assignments = AssignedActivities.objects.filter(activityID = Activities.objects.get(activityName = request.POST['activity']))
            for si in studentList:
                studentID = Student.objects.get(pk = si)
                noStudent = True
                # If at least one activity of that name is saved in AssignedActivities (AH)
                if(assignments):
                    # Loop through and check if the assigned activity and student is in the AssignedActivities (AH)
                    for assign in assignments:
                        if assign.recipientStudentID == studentID:
                            # Override the activity with the points (AH)
                            assign.pointsReceived = request.POST['points']
                            assign.save()
                            # The student is assigned an activity; no need to create a new one (AH)
                            noStudent = False
                            #Register event for participationNoted
                            register_event(Event.participationNoted, request, assign.recipientStudentID, assign.activityID.activityID)
                            print("Registered Event: Participation Noted Event, Student: " + str(assign.recipientStudentID) + ", Activity Assignment: " + str(assign.activityAssigmentID))
                # If there are no assigned activities of this name or
                # If the student is not assigned to an activity but the activity is assigned to other students (AH)
                if noStudent == True or not assignments:
                    # Create new activity if there are none of this activity type in assigned activities (AH)
                    assignment = AssignedActivities()
                    assignment.activityID = Activities.objects.get(activityName = request.POST['activity'])
                    assignment.recipientStudentID = studentID
                    assignment.pointsReceived = request.POST['points']
                    assignment.save()
                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignment.recipientStudentID, assignment.activityID.activityID)
                    print("Registered Event: Participation Noted Event, Student: " + str(assignment.recipientStudentID) + ", Activity Assignment: " + str(assignment.activityAssigmentID))

    
    # prepare context for Activity Assignment List      
    context_dict = createContextForPointsAssignment()
       
    return redirect('/oneUp/instructors/activitiesList', context_dict)    
        
        
def createContextForPointsAssignment():
    context_dict = { }

    student_Activity_Assignment_ID = []      
    student_ID = []
    student_Name = []
    activity_ID = []
    activity_Name = []
    course_ID = []
    assignment_Timestamp = []
    activity_Score = []
    instructor_Feedback = []
    
        
    assignedActivityScores = StudentActivities.objects.all().order_by('-timestamp')
    
    for assignedScore in assignedActivityScores:
        student_Activity_Assignment_ID.append(assignedScore.studentActivityAssignmentID) #pk
        student_ID.append(assignedScore.studentID) 
        student_Name.append(assignedScore.studentName)
        activity_ID.append(assignedScore.activityID)
        nameOfActivity = Activities.objects.get(pk = assignedScore.activityID)
        activity_Name.append(nameOfActivity)
        course_ID.append(assignedScore.courseID)
        assignment_Timestamp.append(assignedScore.timestamp)
        activity_Score.append(assignedScore.activityScore)
        instructor_Feedback.append(assignedScore.instructorFeedback[:200])
    
      
    # The range part is the index numbers.
    context_dict['assignedActivityPoints_range'] = zip(range(1,assignedActivityScores.count()+1),student_Activity_Assignment_ID,student_ID,student_Name,activity_ID,activity_Name,course_ID,assignment_Timestamp,activity_Score,instructor_Feedback)
    return context_dict

    
@login_required
def assignedPointsList(request):

    context_dict = createContextForPointsAssignment()

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username        

    return render(request,'Instructors/ActivityAssignPointsForm.html', context_dict)

        