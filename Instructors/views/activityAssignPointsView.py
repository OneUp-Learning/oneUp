#
# Created on  11/20/2015
# Dillon Perry, Austin Hodge
#
import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.template.context_processors import request
from django.utils import timezone
from notify.signals import notify

from Badges.enums import Event
from Badges.events import register_event
from Badges.models import CourseConfigParams
from Badges.tasks import refresh_xp
from Instructors.models import Activities, Courses
from Instructors.views.activityListView import createContextForActivityList
from Instructors.views.utils import (current_localtime, initialContextDict,
                                     moveTestStudentObjToBottom)
from oneUp.decorators import instructorsCheck
from Students.models import (Student, StudentActivities, StudentFile,
                             StudentRegisteredCourses)

default_student_points = -1
default_student_bonus = 0


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def activityAssignPointsView(request):
    context_dict, currentCourse = initialContextDict(request)

    if request.method == 'POST':
        # Get all students assigned to the current course (AH)
        studentRCList = StudentRegisteredCourses.objects.filter(
            courseID=currentCourse)

        activity = Activities.objects.get(
            activityID=request.POST['activityID'])

        activityGradedNow = {}
        for studentRC in studentRCList:
            activityGradedNow[studentRC.studentID] = False

        for studentRC in studentRCList:
            # See if a student is graded for this activity (AH)
            # Should only be one match (AH)
            stud_activity = StudentActivities.objects.filter(
                activityID=request.POST['activityID'], studentID=studentRC.studentID.id).first()

            activity_should_be_graded = False
            studentPoints = None
            studentBonus = None
            if f"student_Points{studentRC.studentID.id}" in request.POST and request.POST[f"student_Points{studentRC.studentID.id}"] != "":
                activity_should_be_graded = True
                print("Graded 1")
                studentPoints = Decimal(request.POST[f"student_Points{studentRC.studentID.id}"])

            if f"student_Bonus{studentRC.studentID.id}" in request.POST and request.POST[f"student_Bonus{studentRC.studentID.id}"] != "" and request.POST[f"student_Bonus{studentRC.studentID.id}"] != "0.00":
                activity_should_be_graded = True
                print("Graded")
                studentBonus = Decimal(request.POST[f"student_Bonus{studentRC.studentID.id}"])

            print(studentPoints, studentBonus)
            
            # If student activity has been submitted or graded
            if stud_activity:
                changesNeedSaving = False
                if request.POST[f"student_Feedback{studentRC.studentID.id}"] != stud_activity.instructorFeedback:
                    stud_activity.instructorFeedback = request.POST[f"student_Feedback{studentRC.studentID.id}"]
                    changesNeedSaving = True

                if not activity_should_be_graded:
                    # In this case there is already a grade, but the instructor has now set the grade back to blank (ungraded)
                    # We are treating this as a special case meaning that the instructor wishes to delete the grade.
                    stud_activity.graded = False
                    stud_activity.activityScore = 0
                else:
                    if activity_should_be_graded and studentPoints != None and studentPoints != stud_activity.activityScore:
                        # A score exists and a new score has been assigned.
                        stud_activity.activityScore = studentPoints
                        stud_activity.timestamp = current_localtime()
                        
                        stud_activity.graded = True
                        changesNeedSaving = True
                        activityGradedNow[studentRC.studentID] = True

                    if activity_should_be_graded and studentBonus != None and studentBonus != stud_activity.bonusPointsAwarded:
                        # The bonus has changed.
                        stud_activity.bonusPointsAwarded = studentBonus
                        stud_activity.graded = True
                        changesNeedSaving = True

                if changesNeedSaving:
                    notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                verb=activity.activityName+' has been graded', nf_type='Activity Graded', extra=json.dumps({"course": str(currentCourse.courseID), "name": str(currentCourse.courseName), "related_link": '/oneUp/students/ActivityDescription?activityID='+str(activity.activityID)}))
                    stud_activity.save()
                # Create new assigned activity object for the student if there are points entered to be assigned (AH)
            elif activity_should_be_graded:
                stud_activity = StudentActivities()
                stud_activity.activityID = activity
                stud_activity.studentID = studentRC.studentID

                if studentPoints != None:
                    stud_activity.activityScore = studentPoints
                else:
                    stud_activity.activityScore = 0
                    
                if studentBonus != None:
                    stud_activity.bonusPointsAwarded = studentBonus
                else:
                    stud_activity.bonusPointsAwarded = 0
                
                stud_activity.instructorFeedback = request.POST[f"student_Feedback{studentRC.studentID.id}"]
                stud_activity.graded = True
                stud_activity.timestamp = current_localtime()
                stud_activity.courseID = currentCourse
                
                stud_activity.save()

                notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                            verb=activity.activityName+' has been graded', nf_type='Activity Graded', extra=json.dumps({"course": str(currentCourse.courseID), "name": str(currentCourse.courseName), "related_link": '/oneUp/students/ActivityDescription?activityID='+str(activity.activityID)}))

                activityGradedNow[studentRC.studentID] = True

        # Register event for participationNoted
        for studentRC in studentRCList:
            # if the student is graded for this activity
            if activityGradedNow[studentRC.studentID] == True:
                register_event(Event.participationNoted, request,
                               studentRC.studentID, activity.activityID)
                # Update student xp
                refresh_xp(studentRC)
                print("Registered Event: Participation Noted Event, Student: " +
                      str(studentRC.studentID) + ", Activity Assignment: " + str(activity))

    # prepare context for Activity List
    context_dict = createContextForActivityList(
        request, context_dict, currentCourse)

    return redirect('/oneUp/instructors/activitiesList', context_dict)


def createContextForPointsAssignment(request, context_dict, currentCourse):
    student_ID = []
    student_Name = []
    student_Graded = []
    student_Submission = []
    student_Points = []
    student_Bonus = []
    student_Feedback = []
    student_TextSubmission = []
    File_Name = []
    
    # send formatted student data to be parsed by modals
    student_submission_data = []

    studentCourse = StudentRegisteredCourses.objects.filter(
        courseID=currentCourse).order_by('studentID__user__last_name')

    for stud_course in studentCourse:
        student = stud_course.studentID
        student_ID.append(student.id)
        if student.isTestStudent:
            student_Name.append(f"(Test Student) {student.user.get_full_name()}")
        else:
            student_Name.append(student.user.get_full_name())
        #zipFile_Name.append(student.user.first_name + student.user.last_name + Activities.objects.get(activityID = request.GET['activityID']).activityName + '.zip')

        if StudentActivities.objects.filter(activityID=request.GET['activityID'], studentID=student).exists():
            stud_act = StudentActivities.objects.get(
                activityID=request.GET['activityID'], studentID=student)
            student_Graded.append(stud_act.graded)
            if stud_act.submitted:
                student_Submission.append(stud_act.submissionTimestamp)
            else:
                student_Submission.append("-")

            if not stud_act.graded:
                student_Points.append("")
            else:
                student_Points.append(stud_act.activityScore)
                
            if not stud_act.richTextSubmission:
                student_TextSubmission.append(False)
            else:
                student_TextSubmission.append(stud_act.richTextSubmission)

            student_Bonus.append(stud_act.bonusPointsAwarded)

            student_Feedback.append(stud_act.instructorFeedback)

            studentFile = StudentFile.objects.filter(
                activity=stud_act, studentID=student, latest=True).first()
                
            if studentFile:
                fName = studentFile.fileName
                File_Name.append(fName)
            else:
                File_Name.append(False)

            #zipFile_Name.append(StudentFile.objects.get(activity = stud_act, studentID = student).fileName)
        else:
            student_Graded.append(False)
            student_Submission.append("-")
            student_Points.append("")
            student_Bonus.append("")
            student_Feedback.append("")
            student_TextSubmission.append(False)
            File_Name.append(False)

    context_dict['isVcUsed'] = CourseConfigParams.objects.get(
        courseID=currentCourse).virtualCurrencyUsed
    context_dict['activityID'] = request.GET['activityID']
    context_dict['activity'] = Activities.objects.get(
        activityID=request.GET['activityID'])
    context_dict['student_submission_data'] = student_submission_data
    student_list = list(zip(range(1, len(student_ID)+1), student_ID, student_Name, student_Graded,student_Submission,
                                   student_TextSubmission, student_Points, student_Bonus, student_Feedback, File_Name))
    
    student_list = moveTestStudentObjToBottom(student_list)

    context_dict['assignedActivityPoints_range'] = student_list
    return context_dict


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def assignedPointsList(request):
    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForPointsAssignment(
        request, context_dict, currentCourse)

    return render(request, 'Instructors/ActivityAssignPointsForm.html', context_dict)
