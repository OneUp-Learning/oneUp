'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses
from Students.models import StudentConfigParams,Student,StudentRegisteredCourses, StudentBadges
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from Instructors.views.dynamicLeaderboardView import generateLeaderboards

from Badges.enums import Event
from Badges.models import  CourseConfigParams
from Badges.events import register_event
from django.contrib.auth.decorators import login_required
from Students.views.utils import studentInitialContextDict


@login_required


def StudentCourseHome(request):
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)

    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']
        context_dict['courseId']=request.POST['courseID']
        context_dict['is_test_student'] = sID.isTestStudent
        if sID.isTestStudent:
            context_dict["username"]="Test Student"
    
    if request.GET:
        request.session['currentCourseID'] = request.GET['courseID']
        context_dict['courseId']=request.GET['courseID']
        context_dict['is_test_student'] = sID.isTestStudent
        if sID.isTestStudent:
            context_dict["username"]="Test Student"
            
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
        context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
        context_dict['course_Name'] = currentCourse.courseName
        context_dict['is_test_student'] = sID.isTestStudent
        if sID.isTestStudent:
            context_dict["username"]="Test Student"
        context_dict['courseId'] = currentCourse.courseID
        st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)
        context_dict['avatar'] =  st_crs.avatarImage    
                      
        context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, True, context_dict)  
        context_dict['courseId']=currentCourse.courseID
           
        scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=sID)   
        ##GGM determine if student has leaderboard enabled

        studentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=sID)
        context_dict['studentLeaderboardToggle'] = studentConfigParams.displayLeaderBoard
         
        if len(scparamsList) > 0:
            scparams = scparamsList[0]
            context_dict["displayBadges"]=scparams.displayBadges
            context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
            context_dict["displayClassAverage"]=scparams.displayClassAverage
            context_dict["displayClassSkills"]=scparams.displayClassSkills
            
        
        context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
        studentObkj = Student.objects.get(id=19)
           
    #Trigger Student login event here so that it can be associated with a particular Course
    register_event(Event.userLogin, request, None, None)
    print("User Login event was registered for the student in the request")
    
    return render(request,'Students/StudentCourseHome.html', context_dict)           
    