#
# Created on  11/20/2015
# Dillon Perry, Austin Hodge
#
from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Students.models import StudentRegisteredCourses, Student, StudentFile
from Instructors.models import Courses, Activities
from Instructors.views.utils import utcDate
from Students.models import StudentActivities
from Badges.events import register_event
from Badges.enums import Event
from Instructors.views.activityListView import createContextForActivityList
from django.template.context_processors import request


def activityAssignPointsView(request):   
    
    if request.method == 'POST':
        # Get all students assigned to the current course (AH)
        currentCourse = request.session['currentCourseID']
        studentList = StudentRegisteredCourses.objects.filter(courseID = currentCourse)
        for student in studentList:
            # See if a student is graded for this activity (AH)
            # Should only be one match (AH)
            assignment = StudentActivities.objects.filter(activityID = request.POST['activityID'], studentID = student.studentID.id).first()
            studentPoints = request.POST['student_Points' + str(student.studentID.id)] 
            isGraded = request.POST.get(str(student.studentID.id)+'_points_graded')

            # If student has been previously graded...
            if assignment:
                # Check if the student has points wanting to be assigned (AH)
                
                print("Points: " + str(studentPoints))
                print("Graded: " + str(isGraded))
                
                if not studentPoints == "-1":
                    # Override the activity with the student points (AH)
                    assignment.activityScore = studentPoints
                    assignment.instructorFeedback =  request.POST['student_Feedback' + str(student.studentID.id)]
                    assignment.timestamp = utcDate()
                    assignment.graded = True
                    assignment.save()

                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignment.studentID, assignment.activityID.activityID)
                    print("Registered Event: Participation Noted Event, Student: " + str(assignment.studentID) + ", Activity Assignment: " + str(assignment.studentActivityID))    
            else:
                # Create new assigned activity object for the student if there are points entered to be assigned (AH)
                if not studentPoints == "-1":
                    # Create new activity (AH)
                    assignment = StudentActivities()
                    assignment.activityID = Activities.objects.get(activityID = request.POST['activityID'])
                    assignment.studentID = Student.objects.get(pk = student.studentID.id)
                    assignment.activityScore = studentPoints
                    assignment.timestamp = utcDate()
                    assignment.instructorFeedback =  request.POST['student_Feedback' + str(student.studentID.id)]
                    assignment.courseID = Courses.objects.get(courseID=currentCourse)
                    assignment.graded = True
                    assignment.save()

                    #Register event for participationNoted
                    register_event(Event.participationNoted, request, assignment.studentID, assignment.activityID.activityID)
       
                    print("Registered Event: Participation Noted Event, Student: " + str(assignment.studentID) + ", Activity Assignment: " + str(assignment.studentActivityID))                           
    
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
    File_Name = []
    
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
    
    for stud_course in studentCourse:
        student = stud_course.studentID
        student_ID.append(student.id)
        student_Name.append((student).user.get_full_name())
        
        #zipFile_Name.append(student.user.first_name + student.user.last_name + Activities.objects.get(activityID = request.GET['activityID']).activityName + '.zip')
        
        if (StudentActivities.objects.filter(activityID = request.GET['activityID'], studentID = student)).exists():
            stud_act = StudentActivities.objects.get(activityID = request.GET['activityID'], studentID = student)
            
            if(stud_act.activityScore == 0 and not stud_act.graded):
                student_Points.append("-1")
            else:
                student_Points.append(stud_act.activityScore)
            
            student_Feedback.append(stud_act.instructorFeedback)
            
            studentFile = StudentFile.objects.filter(activity= stud_act, studentID =student, latest=True).first()
            print(studentFile)
            if(studentFile):
                fName = studentFile.fileName
                print(fName)
#                 if(' ' in fName):
#                     fName = "_".join(fName.split())
#                     File_Name.append(fName)
#                     print(fName)
#                 else:
                File_Name.append(fName)
            else:
                File_Name.append(False)

                
            #zipFile_Name.append(StudentFile.objects.get(activity = stud_act, studentID = student).fileName)
        else:
            print('ELSE')
            student_Points.append("-1")
            student_Feedback.append("")
            File_Name.append(False)

        
    context_dict['activityID'] = request.GET['activityID']
    context_dict['activityName'] = Activities.objects.get(activityID = request.GET['activityID']).activityName
    context_dict['assignedActivityPoints_range'] = zip(range(1,len(student_ID)+1),student_ID,student_Name,student_Points, student_Feedback, File_Name)
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



    
    

        