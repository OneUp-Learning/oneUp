'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.instructorCourseHomeView import courseLeaderboard
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from Instructors.views.dynamicLeaderboardView import generateLeaderboards, generateSkillTable
from Students.views.avatarView import checkIfAvatarExist

from Badges.enums import Event
from Badges.models import  CourseConfigParams
from Badges.events import register_event
from django.contrib.auth.decorators import login_required
from Instructors.models import CoursesSkills, Skills
from Students.views.studentCourseHomeView import courseBadges
from Instructors.views.utils import initialContextDict


@login_required
def LeaderboardInstructorsView(request):
    context_dict = { }
    context_dict, currentCourse = initialContextDict(request)
    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']
    
    if request.GET:
        request.session['currentCourseID'] = request.GET['courseID']
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
                      
        context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, False)

        context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
    return render(request,'Instructors/Leaderboard.html', context_dict)