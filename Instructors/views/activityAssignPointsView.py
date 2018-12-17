#
# Created on  11/20/2015
# Dillon Perry, Austin Hodge
#
from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Students.models import StudentRegisteredCourses, Student, StudentFile
from Instructors.models import Courses, Activities
from Instructors.views.utils import utcDate, initialContextDict
from Students.models import StudentActivities
from Badges.events import register_event
from Badges.enums import Event
from Instructors.views.activityListView import createContextForActivityList
from django.template.context_processors import request
from notify.signals import notify
from decimal import Decimal
from oneUp.decorators import instructorsCheck  

default_student_points = -1
default_student_bonus = 0

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def activityAssignPointsView(request):   
    context_dict, currentCourse = initialContextDict(request)

    if request.method == 'POST':
        # Get all students assigned to the current course (AH)
        studentRCList = StudentRegisteredCourses.objects.filter(courseID = currentCourse)
        
        activity = Activities.objects.get(activityID = request.POST['activityID'])
        
        activityGradedNow = { }
        for studentRC in studentRCList:
            activityGradedNow[studentRC.studentID] = False
        
        for studentRC in studentRCList:
            # See if a student is graded for this activity (AH)
            # Should only be one match (AH)
            stud_activity = StudentActivities.objects.filter(activityID = request.POST['activityID'], studentID = studentRC.studentID.id).first()
            studentPoints = Decimal(request.POST['student_Points' + str(studentRC.studentID.id)])
            studentBonus = Decimal(request.POST['student_Bonus' + str(studentRC.studentID.id)])

            # If student has been previously graded...
            if stud_activity:

                if studentPoints == default_student_points:
                    # In this case there is already a grade, but the instructor has now set the grade back to -1 (ungraded)
                    # We are treating this as a special case meaning that the instructor wishes to delete the grade.
                    stud_activity.delete()
                else:
                    changesNeedSaving = False

                    if studentPoints != stud_activity.activityScore:
                        # A score exists and a new score has been assigned.
                        stud_activity.activityScore = studentPoints
                        stud_activity.timestamp = utcDate()
                        stud_activity.instructorFeedback =  request.POST['student_Feedback' + str(studentRC.studentID.id)]
                        stud_activity.graded = True
                        changesNeedSaving = True
                        activityGradedNow[studentRC.studentID] = True

                        notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                    verb= activity.activityName+' has been graded', nf_type='Activity Graded')
                    
                    if studentBonus != stud_activity.bonusPointsAwarded:
                        # The bonus has changed.
                        stud_activity.bonusPointsAwarded = studentBonus
                        changesNeedSaving = True

                    if changesNeedSaving:
                        stud_activity.save()

                stud_activity.timestamp = utcDate()
                stud_activity.graded = True
                stud_activity.save()
                activityGradedNow[studentRC.studentID] = True
    
                actName = activity.activityName
                    
                notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                            verb= actName+' was graded', nf_type='Activity Graded')
            
            else:
                # Create new assigned activity object for the student if there are points entered to be assigned (AH)
                if not studentPoints == default_student_points or not studentBonus == default_student_bonus:
                    stud_activity = StudentActivities()
                    stud_activity.activityID = activity
                    stud_activity.studentID = studentRC.studentID

                    if not studentPoints == default_student_points:
                        stud_activity.activityScore = studentPoints
                        stud_activity.instructorFeedback =  request.POST['student_Feedback' + str(studentRC.studentID.id)]
                    else:
                        stud_activity.activityScore = 0
                        stud_activity.instructorFeedback =  ""
                    
                    stud_activity.bonusPointsAwarded = studentBonus
                    stud_activity.timestamp = utcDate()
                    stud_activity.courseID = currentCourse
                    stud_activity.graded = True
                    stud_activity.save()
                                            
                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb= activity.activityName+' has been graded', nf_type='Activity Graded')

                activityGradedNow[studentRC.studentID] = True
       
        #Register event for participationNoted
        for studentRC in studentRCList:
            # if the student is graded for this activity             
            if activityGradedNow[studentRC.studentID] == True:
                register_event(Event.participationNoted, request, studentRC.studentID, activity.activityID)
                print("Registered Event: Participation Noted Event, Student: " + str(studentRC.studentID) + ", Activity Assignment: " + str(activity))                          
    
    # prepare context for Activity List      
    context_dict = createContextForActivityList(request, context_dict, currentCourse) 
            
    return redirect('/oneUp/instructors/activitiesList', context_dict)    
        
        
def createContextForPointsAssignment(request, context_dict, currentCourse):
    student_ID = []
    student_Name = []
    student_Points = [] 
    student_Bonus = []   
    student_Feedback = []
    File_Name = []
    
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = currentCourse).order_by('studentID__user__last_name')
    
    for stud_course in studentCourse:
        student = stud_course.studentID
        student_ID.append(student.id)
        if student.isTestStudent:
            student_Name.append("Test Student")
        else:
            student_Name.append((student).user.get_full_name())
        
        #zipFile_Name.append(student.user.first_name + student.user.last_name + Activities.objects.get(activityID = request.GET['activityID']).activityName + '.zip')
        
        if (StudentActivities.objects.filter(activityID = request.GET['activityID'], studentID = student)).exists():
            stud_act = StudentActivities.objects.get(activityID = request.GET['activityID'], studentID = student)
            
            if not stud_act.graded:
                student_Points.append(default_student_points)
            else:
                student_Points.append(stud_act.activityScore)

            student_Bonus.append(stud_act.bonusPointsAwarded) 
            
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
            student_Points.append(str(default_student_points))
            student_Bonus.append(str(default_student_bonus))
            student_Feedback.append("")
            File_Name.append(False)

        
    context_dict['activityID'] = request.GET['activityID']
    context_dict['activityName'] = Activities.objects.get(activityID = request.GET['activityID']).activityName
    context_dict['assignedActivityPoints_range'] = list(zip(range(1,len(student_ID)+1),student_ID,student_Name,student_Points, student_Bonus, student_Feedback, File_Name))    
    return context_dict
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def assignedPointsList(request):
    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForPointsAssignment(request, context_dict, currentCourse)

    return render(request,'Instructors/ActivityAssignPointsForm.html', context_dict)
