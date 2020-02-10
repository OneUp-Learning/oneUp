'''
Created on Sep 14, 2016

'''
from django.shortcuts import render,redirect
from Instructors.models import Courses
from Students.models import StudentConfigParams,Student,StudentRegisteredCourses, StudentBadges
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
from Students.views.studentCourseHomeView import studentBadges
from Students.views.utils import studentInitialContextDict

@login_required


def LeaderboardView(request):
    
    cd,currentCourse = studentInitialContextDict(request)
      
    #Redirects students from leaderboard page if leaderboard not enabled
    ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
    leaderboardEnabled=ccparams.leaderboardUsed
    if not leaderboardEnabled:
        return redirect('/oneUp/students/StudentCourseHome')

    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)

    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']
    
    if request.GET:
        request.session['currentCourseID'] = request.GET['courseID']
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
        context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
        context_dict['course_Name'] = currentCourse.courseName
        st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)

        context_dict["gamificationUsed"] = ccparams.gamificationUsed
        context_dict["badgesUsed"]=ccparams.badgesUsed
        context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
        context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
        context_dict["numStudentsDisplayed"]=ccparams.numStudentsDisplayed
        context_dict["numStudentBestSkillsDisplayed"] = ccparams.numStudentBestSkillsDisplayed
        context_dict["numBadgesDisplayed"]=ccparams.numBadgesDisplayed

        context_dict['avatar'] =  checkIfAvatarExist(st_crs)  
   
        context_dict['is_test_student'] = sID.isTestStudent
                      
        context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, False)  
        
        generateSkillTable(currentCourse, context_dict)
               
                  
        scparams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=sID)    
        context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
        context_dict["displayBadges"]=scparams.displayBadges
        context_dict["displayClassSkills"]=scparams.displayClassSkills
            
        
        context_dict['ccparams'] = ccparams
        ##GGM determine if student has leaderboard enabled
        studentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=sID)
        context_dict['studentLeaderboardToggle'] = studentConfigParams.displayLeaderBoard
        context_dict["classSkillsDisplayed"]= studentConfigParams.displayClassSkills
        context_dict['courseBadges'] = studentBadges(currentCourse)
           
    #Trigger Student login event here so that it can be associated with a particular Course
    if not sID.isTestStudent:
        register_event(Event.visitedLeaderboardPage, request, sID, None)
    print("User visited Leaderboard page was registered for the student in the request")
    return render(request,'Students/Leaderboard.html', context_dict)