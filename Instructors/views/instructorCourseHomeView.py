'''
Created on Sep 10, 2016
Last Updated Sep 14, 2017

'''
from django.shortcuts import render
from Instructors.models import Challenges
from Instructors.models import Skills, CoursesSkills, Activities
from Badges.models import CourseConfigParams
from Students.models import StudentBadges,StudentChallenges, StudentCourseSkills, StudentRegisteredCourses,StudentActivities
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from Instructors.views.dynamicLeaderboardView import generateLeaderboards, generateSkillTable
from Instructors.views.utils import initialContextDict
from Students.views.avatarView import checkIfAvatarExist

from datetime import datetime
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck  
import inspect
import logging
logger = logging.getLogger(__name__)

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def studentXP(studentId, courseId):

    xpWeightSP = 0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    xpSeriousMaxScore = True # Specify if the xp should be calculated based on max score or first attempt
    xpWarmupMaxScore = True

    ccparamsList = CourseConfigParams.objects.filter(courseID=courseId)
    if len(ccparamsList) >0:
        cparams = ccparamsList[0]
        xpWeightSP=cparams.xpWeightSP
        xpWeightSChallenge=cparams.xpWeightSChallenge
        xpWeightWChallenge=cparams.xpWeightWChallenge
        xpWeightAPoints=cparams.xpWeightAPoints
        xpSeriousMaxScore = cparams.xpCalculateSeriousByMaxScore 
        xpWarmupMaxScore = cparams.xpCalculateWarmupByMaxScore 

    #print("From StudentCourseHome, Config Parameters::",xpWeightSP,xpWeightSChallenge,xpWeightWChallenge,xpWeightAPoints)
    
    # XP Points Variable initialization
    xp = 0       
    # get the serious challenges for this course
    
    earnedScorePoints = 0 
    totalScorePoints = 0   
    courseChallenges = Challenges.objects.filter(courseID=courseId, isGraded=True, isVisible=True)
    for challenge in courseChallenges:
        sc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)

        gradeID  = [] 
        if xpSeriousMaxScore:                           
            for s in sc:
                gradeID.append(int(s.getScoreWithBonus()))   # get the score + adjustment + bonus
        elif sc.exists():
            gradeID.append(int(sc.first().getScoreWithBonus())) 
                                
        if(gradeID):
            if xpSeriousMaxScore:
                earnedScorePoints += max(gradeID)
            else:
                earnedScorePoints += gradeID[0]

            totalScorePoints += challenge.totalScore
            
    totalScorePointsSC = earnedScorePoints * xpWeightSChallenge / 100      # max grade for this challenge
    print("Total Points SC {}".format(totalScorePointsSC))
    # get the warm up challenges for this course
    
    earnedScorePoints = 0 
    totalScorePoints = 0   
    
    courseChallenges = Challenges.objects.filter(courseID=courseId, isGraded=False, isVisible=True)
    for challenge in courseChallenges:
        wc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)

        gradeID  = []  
        if xpWarmupMaxScore:                          
            for w in wc:
                gradeID.append(int(w.testScore)) 
        elif wc.exists():
            gradeID.append(int(wc.first().testScore))
                               
        if(gradeID):
            if xpWarmupMaxScore:
                earnedScorePoints += max(gradeID)
            else:
                earnedScorePoints += gradeID[0]

            totalScorePoints += challenge.totalScore
            
    totalScorePointsWC = earnedScorePoints * xpWeightWChallenge / 100      # max grade for this challenge
                        
    # get the activity points for this course

    earnedActivityPoints = 0
    totalActivityPoints = 0

    courseActivities = Activities.objects.filter(courseID=courseId)
    for activity in courseActivities:

        sa = StudentActivities.objects.filter(studentID=studentId, courseID=courseId,activityID=activity)

        gradeID  = []                            
        for a in sa:
            gradeID.append(int(a.getScoreWithBonus())) 
                               
        if(gradeID):
            earnedActivityPoints += max(gradeID)
            totalActivityPoints += a.activityID.points
            
    totalScorePointsAP = earnedActivityPoints * xpWeightAPoints / 100
            
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
            totalScorePointsSP = (sum(gradeID)* xpWeightSP / 100)

    xp = round((totalScorePointsSC + totalScorePointsWC + totalScorePointsSP + totalScorePointsAP),0)

    return xp

def courseLeaderboard(currentCourse, context_dict):
    
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
            N = 7
            
            date_N_days_ago = datetime.now() - timedelta(days=N)

            students = []                                         
            for st_c in st_crs:
                students.append(st_c.studentID)     # all students in the course
            
            #Displaying the list of challenges from database
            badges = StudentBadges.objects.all().order_by('-timestamp')
            print("badges")
            print(badges)
            for badge in badges:
                if (badge.studentID in students) and (badge.badgeID.courseID == currentCourse):
                    studentBadgeID.append(badge.studentBadgeID)
                    studentID.append(badge.studentID)
                    badgeID.append(badge.badgeID)
                    badgeName.append(badge.badgeID.badgeName)
                    badgeImage.append(badge.badgeID.badgeImage)
                    st_crs = StudentRegisteredCourses.objects.get(studentID=badge.studentID,courseID=currentCourse)       
                    avatarImage.append(checkIfAvatarExist(st_crs)) 
                    student = badge.studentID
                    if not (student.user.first_name and student.user.last_name):
                        studentUser.append(student.user)
                    else:
                        studentUser.append(student.user.first_name +" " + student.user.last_name)
                  
                              
            print("cparams")
            print(ccparams.numBadgesDisplayed+1)                    
            context_dict['badgesInfo'] = zip(range(1,ccparams.numBadgesDisplayed+1),studentBadgeID,studentID,badgeID, badgeName, badgeImage,avatarImage, studentUser)
                
            #user range here is comprised of zip(leaderboardNames, leaderboardDescriptions, leaderboardRankings)
            #leaderboard rankings is also a zip #GGM
            context_dict['leaderboard_range'] = generateLeaderboards(currentCourse, True)   
            generateSkillTable(currentCourse, context_dict)            
                       
        else:
            context_dict['course_Name'] = 'Not Selected'
        
    return context_dict
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def instructorCourseHome(request):
    
    context_dict, currentCourse = initialContextDict(request)
            
    context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
    context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
    context_dict['course_Name'] = currentCourse.courseName
    context_dict['course_id'] = currentCourse.courseID

    context_dict = courseLeaderboard(currentCourse, context_dict)
        
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)
