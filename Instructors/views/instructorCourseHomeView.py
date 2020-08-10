'''
Created on Sep 10, 2016
Last Updated Sep 14, 2017

'''
from django.shortcuts import render
from Instructors.models import Challenges
from Instructors.models import Skills, CoursesSkills, Activities
from Badges.models import CourseConfigParams
from Students.models import StudentBadges, StudentChallenges, StudentCourseSkills, StudentRegisteredCourses, StudentActivities
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from Instructors.views.dynamicLeaderboardView import generateLeaderboards, generateSkillTable
from Instructors.views.utils import initialContextDict
from Students.views.avatarView import checkIfAvatarExist

from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck
import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def courseLeaderboard(currentCourse, context_dict):

    # Check if there are students in this course
    students_registered_in_course = StudentRegisteredCourses.objects.filter(
        courseID=currentCourse).exclude(studentID__isTestStudent=True)

    if students_registered_in_course:
        if currentCourse:
            ccparamsList = CourseConfigParams.objects.filter(
                courseID=currentCourse)
            if len(ccparamsList) > 0:
                ccparams = ccparamsList[0]
                context_dict["gamificationUsed"] = ccparams.gamificationUsed
                context_dict["badgesUsed"] = ccparams.badgesUsed
                context_dict["leaderboardUsed"] = ccparams.leaderboardUsed
                context_dict["classSkillsDisplayed"] = ccparams.classSkillsDisplayed
                context_dict["numStudentsDisplayed"] = ccparams.numStudentsDisplayed
                context_dict["numStudentBestSkillsDisplayed"] = ccparams.numStudentBestSkillsDisplayed
                context_dict["numBadgesDisplayed"] = ccparams.numBadgesDisplayed

            badgeId = []
            studentBadgeID = []
            studentID = []
            badgeID = []
            badgeName = []
            badgeImage = []
            avatarImage = []
            studentUser = []

            students = []
            for student_in_course in students_registered_in_course:
                # all students in the course
                students.append(student_in_course.studentID)

            # Displaying the badges for this one class from database
            badges = StudentBadges.objects.filter(badgeID__courseID=currentCourse).order_by('-timestamp')
            for badge in badges:
                if (badge.studentID in students):
                    studentBadgeID.append(badge.studentBadgeID)
                    studentID.append(badge.studentID)
                    badgeID.append(badge.badgeID)
                    badgeName.append(badge.badgeID.badgeName)
                    badgeImage.append(badge.badgeID.badgeImage)
                    students_registered_in_course = StudentRegisteredCourses.objects.get(
                        studentID=badge.studentID, courseID=currentCourse)
                    avatarImage.append(checkIfAvatarExist(students_registered_in_course))
                    student = badge.studentID
                    if student.user:
                        if not (student.user.first_name and student.user.last_name):
                            studentUser.append(student.user)
                        else:
                            studentUser.append(
                                student.user.first_name + " " + student.user.last_name)

            context_dict['badgesInfo'] = zip(range(1, ccparams.numBadgesDisplayed+1), studentBadgeID,
                                             studentID, badgeID, badgeName, badgeImage, avatarImage, studentUser)

            # user range here is comprised of zip(leaderboardNames, leaderboardDescriptions, leaderboardRankings)
            # leaderboard rankings is also a zip #GGM

            context_dict['leaderboard_range'] = generateLeaderboards(
                currentCourse, True)
            generateSkillTable(currentCourse, context_dict)

        else:
            context_dict['course_Name'] = 'Not Selected'

    return context_dict


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def instructorCourseHome(request):

    context_dict, currentCourse = initialContextDict(request)

    context_dict = createContextForAnnouncementList(
        currentCourse, context_dict, True)
    context_dict = createContextForUpcommingChallengesList(
        currentCourse, context_dict)
    context_dict['course_Name'] = currentCourse.courseName
    context_dict['course_id'] = currentCourse.courseID

    context_dict = courseLeaderboard(currentCourse, context_dict)
    return render(request, 'Instructors/InstructorCourseHome.html', context_dict)
