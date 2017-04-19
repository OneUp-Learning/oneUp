'''
Created on Sep 10, 2016
Last Updated Sep 12, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses, Challenges
from Instructors.models import Skills, CoursesSkills 
from Badges.models import CourseConfigParams
from Students.models import StudentBadges,StudentChallenges, StudentCourseSkills, StudentRegisteredCourses
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from _datetime import datetime
from datetime import timedelta

import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def studentXP(studentId, courseId, courseChallenges):
    
    xp = 0
    print(studentId)
    print(courseId)
    print(courseChallenges)
    for challenge in courseChallenges:
        sc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)
        print(sc)
        gradeID  = []
                            
        for c in sc:
            gradeID.append(int(c.testScore)) 
            print(c.testScore)                                
        if(gradeID):
            xp = xp + max(gradeID)      # max grade for this challenge

    print(str(xp))
    return xp

def courseLeaderboard(currentCourse, context_dict):
    
    # Check if there are students in this course
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    if st_crs:
        if currentCourse:
            ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
                
            if len(ccparamsList) > 0:
                ccparams = ccparamsList[0] 
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
            N = 7
            
            date_N_days_ago = datetime.now() - timedelta(days=N)
    
            #Displaying the list of challenges from database
            badges = StudentBadges.objects.all().order_by('-timestamp')
           
            for badge in badges:
                studentBadgeID.append(badge.studentBadgeID)
                studentID.append(badge.studentID)
                badgeID.append(badge.badgeID)
                badgeName.append(badge.badgeID.badgeName)
                badgeImage.append(badge.badgeID.badgeImage)
                st_crs = StudentRegisteredCourses.objects.get(studentID=badge.studentID,courseID=currentCourse)                
                avatarImage.append(st_crs.avatarImage)
                              
            # The range part is the index numbers.
            context_dict['badgesInfo'] = zip(range(1,ccparams.numBadgesDisplayed+1),studentBadgeID,studentID,badgeID,badgeImage,avatarImage)
    
            students = []
            st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)                                           
            for st_c in st_crs:
                students.append(st_c.studentID)     # all students in the course
                      
            context_dict['skills'] = []
            cskills = CoursesSkills.objects.filter(courseID=currentCourse)
            for sk in cskills:
                skill = Skills.objects.get(skillID=sk.skillID.skillID)
    
                usersInfo=[] 
                                                 
                for u in students:
                    skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=u,skillID = skill)
                    skillPoints =0 ;
                                                         
                    for sRecord in skillRecords:
                        skillPoints += sRecord.skillPoints
                    if skillPoints > 0:
                        uSkillInfo = {'user':u.user,'skillPoints':skillPoints,'avatarImage':st_c.avatarImage}
                        print("userSkillLst",lineno(),uSkillInfo)
                        #Sort and Splice here
                        usersInfo.append(uSkillInfo) 
                skillInfo = {'skillName':skill.skillName,'usersInfo':usersInfo[0:ccparams.numStudentsDisplayed]}
                print("skillInfo",lineno(),skillInfo)
                context_dict['skills'].append(skillInfo)
          
            # XP Points
        
            # get the challenges for this course
            courseChallenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True)
    
            # dictionary studentAvatar - XP
            studentXP_dict = {}
            for s in students:
                sXP = studentXP(s, currentCourse, courseChallenges)
                st_crs = StudentRegisteredCourses.objects.get(studentID=s,courseID=currentCourse)
                studentXP_dict[st_crs.avatarImage] = sXP 
                
            # sort the dictionary by its values; the result is a list of pairs (key, value)
            xp_pairs = sorted(studentXP_dict.items(), key=lambda x: x[1], reverse=True)
            xp_pairs = xp_pairs[:ccparams.numStudentsDisplayed]
            
            avatarImage = []
            xpoints = []
            for item in xp_pairs:
                if item[1] > 0:         # don't append if 0 XP points
                    avatarImage.append(item[0])
                    xpoints.append(item[1])
            
            context_dict['user_range'] = zip(range(1,ccparams.numStudentsDisplayed+1),avatarImage, xpoints)                 
                       
        else:
            context_dict['course_Name'] = 'Not Selected'
        
    return context_dict
    

def instructorCourseHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    if request.GET:
        request.session['currentCourseID'] = request.GET['courseID']
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
        context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
        context_dict['course_Name'] = currentCourse.courseName
        
    context_dict = courseLeaderboard(currentCourse, context_dict)
        
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)
