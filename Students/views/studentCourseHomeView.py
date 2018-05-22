'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses
from Students.models import StudentConfigParams,Student,StudentRegisteredCourses, StudentBadges
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.instructorCourseHomeView import courseLeaderboard
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList

from Badges.enums import Event
from Badges.models import  CourseConfigParams
from Badges.events import register_event
from django.contrib.auth.decorators import login_required

@login_required


def StudentCourseHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
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
        context_dict['avatar'] =  st_crs.avatarImage    
                      
        context_dict = courseLeaderboard(currentCourse, context_dict)
           
        scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=sID)    
        if len(scparamsList) > 0:
            scparams = scparamsList[0]
            context_dict["displayBadges"]=scparams.displayBadges
            context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
            context_dict["displayClassAverage"]=scparams.displayClassAverage
            context_dict["displayClassSkills"]=scparams.displayClassSkills
            
        
        context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
           
    #Trigger Student login event here so that it can be associated with a particular Course
    register_event(Event.userLogin, request, None, None)
    print("User Login event was registered for the student in the request")
    
    return render(request,'Students/StudentCourseHome.html', context_dict)           
        