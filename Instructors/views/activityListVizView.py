'''
Created on March 11, 2015

@author: dichevad
'''
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from Instructors.models import Activities, Courses
from Students.models import StudentRegisteredCourses, Student
from Instructors.models import AssignedActivities

def createContextForActivityList(request):
    context_dict = { }

    activity_ID = []      
    activity_Name = []         
    description = []
    points = []
     
    student_ID = []    
    student_Name = []    
    activityCount = 0
   
        
    activities = Activities.objects.all()
    for activity in activities:
        activity_ID.append(activity.activityID) #pk
        activity_Name.append(activity.activityName)
        description.append(activity.description[:100])
        points.append(activity.points)
        activityCount +=1
    print (str(activityCount))       
    # The range part is the index numbers.
    context_dict['activity_range'] = zip(range(1,activities.count()+1),activity_ID,activity_Name,description,points)
    context_dict['activityCount'] = activityCount
    #Get StudentID and StudentName for every student in the current course
    #This context_dict is used to populate the scrollable check list for student names
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
    for entry in studentCourse:
        student_ID.append(entry.studentID.id)
        student_Name.append((entry.studentID).user.get_full_name())
    context_dict['student_select_range'] = zip(student_ID,student_Name)
    context_dict['activity_select_range'] = zip(activity_ID, activity_Name)
    
    
    
    #Assignment History Section
    assignment_ID = []
    assignment_Name = []
    assignment_Recipient = []
    assignment_Points = []
    
    assignments = AssignedActivities.objects.all().order_by('-activityAssigmentID')
    for assignment in assignments:
        assignment_ID.append(assignment.activityAssigmentID) #pk
        assignment_Name.append(assignment.activityID.activityName)
        assignment_Recipient.append(assignment.recipientStudentID)
        assignment_Points.append(assignment.pointsReceived)
    context_dict['assignment_history_range'] = zip(range(1,assignments.count()+1),assignment_Name,assignment_Recipient,assignment_Points, assignment_ID)

    return context_dict

    
@login_required
def activityListViz(request):

    context = RequestContext(request)
    context_dict = createContextForActivityList(request)

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        

    return render_to_response('Instructors/ClassActivityAchievementsViz.html', context_dict, context)
