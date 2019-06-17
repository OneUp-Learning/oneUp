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

from Students.views.avatarView import checkIfAvatarExist

from Students.views.goalsListView import createContextForGoalsList
from Students.models import StudentGoalSetting
from Badges.enums import Goal
from Badges import systemVariables
from Students.views import goalCreateView

@login_required
def StudentCourseHome(request):
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)

    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']
        context_dict['course_id']=request.POST['courseID']
        context_dict['is_test_student'] = sID.isTestStudent
        if sID.isTestStudent:
            context_dict["username"]="Test Student"
    
    if request.GET:
        request.session['currentCourseID'] = request.GET['courseID']
        context_dict['course_id']=request.GET['courseID']
        context_dict['is_test_student'] = sID.isTestStudent
        if sID.isTestStudent:
            context_dict["username"]="Test Student"
                
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
        context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
        context_dict = createContextForGoalsList(currentCourse, context_dict, True, request.user)
        context_dict['course_Name'] = currentCourse.courseName
        context_dict['is_test_student'] = sID.isTestStudent
        if sID.isTestStudent:
            context_dict["username"]="Test Student"
        context_dict['course_id'] = currentCourse.courseID
        st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)
        context_dict['avatar'] =  st_crs.avatarImage    
        
        context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, True)  
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
            context_dict["displayGoal"]=scparams.displayGoal
        
        context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
        context_dict = courseBadges(currentCourse, context_dict)
           
    #Trigger Student login event here so that it can be associated with a particular Course
    register_event(Event.userLogin, request, None, None)
    print("User Login event was registered for the student in the request")
    return render(request,'Students/StudentCourseHome.html', context_dict)          

def courseBadges(currentCourse, context_dict):
    
    # Check if there are students in this course
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)

    if st_crs:
        if currentCourse:
            ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
            if len(ccparamsList) > 0:
                ccparams = ccparamsList[0] 
                context_dict["gamificationUsed"] = ccparams.gamificationUsed
                context_dict["badgesUsed"]=ccparams.badgesUsed
                context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
                context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
                context_dict["numStudentsDisplayed"]=ccparams.numStudentsDisplayed
                context_dict["numStudentBestSkillsDisplayed"] = ccparams.numStudentBestSkillsDisplayed
                context_dict["numBadgesDisplayed"]=ccparams.numBadgesDisplayed
            
            badgeId = [] 
            studentBadgeID=[]
            studentID=[]
            badgeID=[]
            badgeName=[]
            badgeImage = []
            avatarImage =[]
            studentUser = []

            students = []                                         
            for st_c in st_crs:
                students.append(st_c.studentID)     # all students in the course
            print("students", students)
            
            #Displaying the list of challenges from database
            badges = StudentBadges.objects.filter(badgeID__courseID=currentCourse).order_by('-timestamp')
            print("badges")
            print(badges)
            for badge in badges:
                if (badge.studentID in students):
                    studentBadgeID.append(badge.studentBadgeID)
                    studentID.append(badge.studentID)
                    badgeID.append(badge.badgeID)
                    badgeName.append(badge.badgeID.badgeName)
                    badgeImage.append(badge.badgeID.badgeImage)
                    st_crs = StudentRegisteredCourses.objects.get(studentID=badge.studentID,courseID=currentCourse)       
                    avatarImage.append(checkIfAvatarExist(st_crs)) 
                  
                              
            print("cparams")
            print(ccparams.numBadgesDisplayed+1)                    
            context_dict['badgesInfo'] = zip(range(1,ccparams.numBadgesDisplayed+1),studentBadgeID,studentID,badgeID, badgeName, badgeImage,avatarImage)
            print("badgesinfo", studentBadgeID,studentID,badgeID, badgeName, badgeImage,avatarImage)
        else:
            context_dict['course_Name'] = 'Not Selected'
        
    return context_dict 

