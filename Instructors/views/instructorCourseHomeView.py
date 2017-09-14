'''
Created on Sep 10, 2016
Last Updated Sep 14, 2017

'''
from django.shortcuts import render
from Instructors.models import Courses, Challenges
from Instructors.models import Skills, CoursesSkills, Activities
from Badges.models import CourseConfigParams
from Students.models import StudentBadges,StudentChallenges, StudentCourseSkills, StudentRegisteredCourses,StudentActivities
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from datetime import datetime, timedelta


import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def studentXP(studentId, courseId):

    xpWeightSP = 0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    ccparamsList = CourseConfigParams.objects.filter(courseID=courseId)
    if len(ccparamsList) >0:
        cparams = ccparamsList[0]
        xpWeightSP=cparams.xpWeightSP
        xpWeightSChallenge=cparams.xpWeightSChallenge
        xpWeightWChallenge=cparams.xpWeightWChallenge
        xpWeightAPoints=cparams.xpWeightAPoints
    #print("From StudentCourseHome, Config Parameters::",xpWeightSP,xpWeightSChallenge,xpWeightWChallenge,xpWeightAPoints)
    
    # XP Points Variable initialization
    xp = 0       
    # get the serious challenges for this course
    totalScorePointsSC = 0
    courseChallenges = Challenges.objects.filter(courseID=courseId, isGraded=True, isVisible=True)
    for challenge in courseChallenges:
        sc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)
        #print(sc)
        gradeID  = []
                            
        for s in sc:
            gradeID.append(int(s.testScore)) 
            #print(s.testScore)                                
        if(gradeID):
            totalScorePointsSC = ((totalScorePointsSC + max(gradeID)) * xpWeightSChallenge / 100)      # max grade for this challenge
    
    # get the warm up challenges for this course
    totalScorePointsWC = 0
    courseChallenges = Challenges.objects.filter(courseID=courseId, isGraded=False, isVisible=True)
    for challenge in courseChallenges:
        wc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)
        #print(wc)
        gradeID  = []
                            
        for w in wc:
            gradeID.append(int(w.testScore)) 
            #print(w.testScore)                                
        if(gradeID):
            totalScorePointsWC = ((totalScorePointsWC + max(gradeID)) * xpWeightWChallenge / 100)      # max grade for this challenge
            
    # get the activity points for this course
    totalScorePointsAP = 0
    courseActivities = Activities.objects.filter(courseID=courseId)
    for activity in courseActivities:
        sa = StudentActivities.objects.filter(studentID=studentId, courseID=courseId,activityID=activity)
        #print("SA",sa)
        gradeID  = []
                            
        for a in sa:
            gradeID.append(int(a.activityScore)) 
            #print(a.activityScore)                                
        if(gradeID):
            totalScorePointsAP = ((totalScorePointsAP + max(gradeID)) * xpWeightAPoints / 100)      # max grade for this challenge
            
    # get the skill points for this course
    totalScorePointsSP = 0
    cskills = CoursesSkills.objects.filter(courseID=courseId)
    for sk in cskills:
        skill = Skills.objects.get(skillID=sk.skillID.skillID)
        
        sp = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId,skillID = skill)
        #print ("Skill Points Records", sp)
        gradeID = []
        
        for p in sp:
            gradeID.append(int(p.skillPoints))
            #print("skillPoints", p.skillPoints)
        if (gradeID):
            totalScorePointsSP = ((totalScorePointsSP + sum(gradeID,0)) * xpWeightSP / 100)

    xp = round((totalScorePointsSC + totalScorePointsWC + totalScorePointsSP + totalScorePointsAP),0)

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

            students = []                                         
            for st_c in st_crs:
                students.append(st_c.studentID)     # all students in the course
            
            #Displaying the list of challenges from database
            badges = StudentBadges.objects.all().order_by('-timestamp')
           
            for badge in badges:
                if badge.studentID in students:
                    studentBadgeID.append(badge.studentBadgeID)
                    studentID.append(badge.studentID)
                    badgeID.append(badge.badgeID)
                    badgeName.append(badge.badgeID.badgeName)
                    badgeImage.append(badge.badgeID.badgeImage)
                    st_crs = StudentRegisteredCourses.objects.get(studentID=badge.studentID,courseID=currentCourse)                
                    avatarImage.append(st_crs.avatarImage)
                              
            context_dict['badgesInfo'] = zip(range(1,ccparams.numBadgesDisplayed+1),studentBadgeID,studentID,badgeID,badgeImage,avatarImage)
    
                      
            context_dict['skills'] = []
            cskills = CoursesSkills.objects.filter(courseID=currentCourse)
            for sk in cskills:
                skill = Skills.objects.get(skillID=sk.skillID.skillID)
    
                usersInfo=[] 
                                                 
                for u in students:
                    skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=u,skillID = skill)
                    skillPoints =0 
                                                         
                    for sRecord in skillRecords:
                        skillPoints += sRecord.skillPoints

                    if skillPoints > 0:
                        st_c = StudentRegisteredCourses.objects.get(studentID=u,courseID=currentCourse)                                       
                        uSkillInfo = {'user':u.user,'skillPoints':skillPoints,'avatarImage':st_c.avatarImage}
                        usersInfo.append(uSkillInfo)
                         
                skillInfo = {'skillName':skill.skillName,'usersInfo':usersInfo[0:ccparams.numStudentsDisplayed]}
                context_dict['skills'].append(skillInfo)
          
#             # XP Points       
#             # get the challenges for this course
#             courseChallenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True)
    
            # dictionary studentAvatar - XP
            studentXP_dict = {}
            for s in students:
                sXP = studentXP(s, currentCourse)
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
