'''
Created on Sep 14, 2016

'''
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from Badges.enums import Event
from Badges.events import register_event
from Badges.models import CourseConfigParams
from Instructors.models import Courses, CoursesSkills, Skills
from Instructors.views.announcementListView import \
    createContextForAnnouncementList
from Instructors.views.dynamicLeaderboardView import (generateLeaderboards,
                                                      generateSkillTable)
from Instructors.views.instructorCourseHomeView import courseLeaderboard
from Instructors.views.upcommingChallengesListView import \
    createContextForUpcommingChallengesList
from Students.models import (Student, StudentBadges, StudentConfigParams,
                             StudentRegisteredCourses)
from Students.views.avatarView import checkIfAvatarExist
from Students.views.studentCourseHomeView import studentBadges
from Students.views.utils import studentInitialContextDict


@login_required
def LeaderboardView(request):
    
    context_dict, currentCourse = studentInitialContextDict(request)
    
    context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, False)  
    
    generateSkillTable(currentCourse, context_dict)
        
    #Trigger Student login event here so that it can be associated with a particular Course
    if not context_dict['is_test_student']:
        register_event(Event.visitedLeaderboardPage, request, context_dict['student'], None)
        
    return render(request,'Students/Leaderboard.html', context_dict)
