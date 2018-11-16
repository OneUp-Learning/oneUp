'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses
from Students.models import StudentConfigParams,Student,StudentRegisteredCourses, StudentBadges
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.instructorCourseHomeView import courseLeaderboard
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from Instructors.views.dynamicLeaderboardView import generateLeaderboards
from Students.views.avatarView import checkIfAvatarExist

from Badges.enums import Event
from Badges.models import  CourseConfigParams
from Badges.events import register_event
from django.contrib.auth.decorators import login_required


@login_required


def LeaderboardView(request):
 
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

        context_dict['avatar'] =  checkIfAvatarExist(st_crs)  
   
        context_dict['is_test_student'] = sID.isTestStudent
                      
        context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, False, context_dict)  
        
        
           
        scparams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=sID)    
        context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
        context_dict["displayBadges"]=scparams.displayBadges
        context_dict["displayClassSkills"]=scparams.displayClassSkills
            
        
        context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
        ##GGM determine if student has leaderboard enabled
        studentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=sID)
        context_dict['studentLeaderboardToggle'] = studentConfigParams.displayLeaderBoard
        print("class skills")
        context_dict["displayClassSkills"]= studentConfigParams.displayClassSkills
        
        
           
    #Trigger Student login event here so that it can be associated with a particular Course
    register_event(Event.visitedLeaderboardPage, request, sID, None)
    print("User visited Leaderboard page was registered for the student in the request")
    
    return render(request,'Students/Leaderboard.html', context_dict)           
        