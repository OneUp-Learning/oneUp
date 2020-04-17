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
from Instructors.views.utils import current_localtime, initialContextDict
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
            studentPoints = Decimal(
                request.POST['student_Points' + str(studentRC.studentID.id)])
            if 'student_Bonus' + str(studentRC.studentID.id) in request.POST:
                studentBonus = Decimal(
                    request.POST['student_Bonus' + str(studentRC.studentID.id)])
            else:
                studentBonus = 0

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
                        stud_activity.timestamp = current_localtime() # TODONE: Use current localtime
                        print(f'{timezone.get_default_timezone_name()} {timezone.now()}')
                        print(f'{timezone.get_current_timezone_name()} {timezone.localtime(timezone.now())}')
                        print(f'{activity.startTimestamp} {timezone.localtime(activity.startTimestamp)}')
                        print(f'{activity.endTimestamp} {timezone.localtime(activity.endTimestamp)}')
                        print(f"converted 2020-04-01 00:43:06.958951 {timezone.make_aware(datetime.strptime('2020-04-01 00:43:06.958951', '%Y-%m-%d %H:%M:%S.%f'))} \n\n")
                        stud_activity.instructorFeedback = request.POST['student_Feedback' + str(
                            studentRC.studentID.id)]
                        stud_activity.graded = True
                        changesNeedSaving = True
                        activityGradedNow[studentRC.studentID] = True

                    if studentBonus != stud_activity.bonusPointsAwarded:
                        # The bonus has changed.
                        stud_activity.bonusPointsAwarded = studentBonus
                        changesNeedSaving = True

                    if changesNeedSaving:
                        notify.send(None, recipient=studentRC.studentID.user, actor=request.user,
                                    verb=activity.activityName+' has been graded', nf_type='Activity Graded', extra=json.dumps({"course": str(currentCourse.courseID), "name": str(currentCourse.courseName), "related_link": '/oneUp/students/ActivityDescription?activityID='+str(activity.activityID)}))
                        stud_activity.save()
                # Create new assigned activity object for the student if there are points entered to be assigned (AH)
            elif not studentPoints == default_student_points or not studentBonus == default_student_bonus:
                stud_activity = StudentActivities()
                stud_activity.activityID = activity
                stud_activity.studentID = studentRC.studentID

                if not studentPoints == default_student_points:
                    stud_activity.activityScore = studentPoints
                    stud_activity.instructorFeedback = request.POST['student_Feedback' + str(
                        studentRC.studentID.id)]
                else:
                    stud_activity.activityScore = 0
                    stud_activity.instructorFeedback = ""

                stud_activity.bonusPointsAwarded = studentBonus
                stud_activity.timestamp = current_localtime() #TODONE:timezone.localtime(timezone.now())
                stud_activity.courseID = currentCourse
                stud_activity.graded = True
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
    student_first_name = []
    student_last_name = []
    student_Points = []
    student_Bonus = []
    student_Feedback = []
    File_Name = []

    studentCourse = StudentRegisteredCourses.objects.filter(
        courseID=currentCourse).order_by('studentID__user__last_name')

    for stud_course in studentCourse:
        student = stud_course.studentID
        student_ID.append(student.id)
        if student.isTestStudent:
            student_first_name.append("Test")
            student_last_name.append("Student")
        else:
            student_first_name.append((student).user.first_name)
            student_last_name.append((student).user.last_name)
        #zipFile_Name.append(student.user.first_name + student.user.last_name + Activities.objects.get(activityID = request.GET['activityID']).activityName + '.zip')

        if (StudentActivities.objects.filter(activityID=request.GET['activityID'], studentID=student)).exists():
            stud_act = StudentActivities.objects.get(
                activityID=request.GET['activityID'], studentID=student)

            if not stud_act.graded:
                student_Points.append(default_student_points)
            else:
                student_Points.append(stud_act.activityScore)

            student_Bonus.append(stud_act.bonusPointsAwarded)

            student_Feedback.append(stud_act.instructorFeedback)

            studentFile = StudentFile.objects.filter(
                activity=stud_act, studentID=student, latest=True).first()
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

    context_dict['isVcUsed'] = CourseConfigParams.objects.get(
        courseID=currentCourse).virtualCurrencyUsed
    context_dict['activityID'] = request.GET['activityID']
    context_dict['activityName'] = Activities.objects.get(
        activityID=request.GET['activityID']).activityName

    student_list = sorted(list(zip(range(1, len(student_ID)+1), student_ID, student_first_name, student_last_name,
                                   student_Points, student_Bonus, student_Feedback, File_Name)), key=lambda tup: tup[3])
    # we have to find the index for the test student and remove them from the sorted list
    test_index = [y[2] for y in student_list].index('Test')
    test_student_ob = student_list[test_index]
    del student_list[test_index]

    # then we insert them back into the list at the very end where they belong
    student_list.append(test_student_ob)

    context_dict['assignedActivityPoints_range'] = student_list
    return context_dict


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def assignedPointsList(request):
    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForPointsAssignment(
        request, context_dict, currentCourse)

    return render(request, 'Instructors/ActivityAssignPointsForm.html', context_dict)
