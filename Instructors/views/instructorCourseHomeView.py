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
from Instructors.views.dynamicLeaderboardView import generateLeaderboards
from Instructors.views.utils import initialContextDict
from Students.views.avatarView import checkIfAvatarExist

from datetime import datetime
from datetime import timedelta
from django.contrib.auth.decorators import login_required

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
    
    earnedScorePoints = 0 
    totalScorePoints = 0   
    
    courseChallenges = Challenges.objects.filter(courseID=courseId, isGraded=True, isVisible=True)
    for challenge in courseChallenges:
        sc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)

        gradeID  = []                            
        for s in sc:
            gradeID.append(int(s.getScoreWithBonus()))   # get the score + adjustment
                                
        if(gradeID):
            earnedScorePoints += max(gradeID)
            totalScorePoints += challenge.totalScore
            
    totalScorePointsSC = earnedScorePoints * xpWeightSChallenge / 100      # max grade for this challenge
    
    # get the warm up challenges for this course
    
    earnedScorePoints = 0 
    totalScorePoints = 0   
    
    courseChallenges = Challenges.objects.filter(courseID=courseId, isGraded=False, isVisible=True)
    for challenge in courseChallenges:
        wc = StudentChallenges.objects.filter(studentID=studentId, courseID=courseId,challengeID=challenge)

        gradeID  = []                            
        for w in wc:
            gradeID.append(int(w.testScore)) 
                               
        if(gradeID):
            earnedScorePoints += max(gradeID)
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
            totalScorePointsSP = ((totalScorePointsSP + sum(gradeID,0)) * xpWeightSP / 100)

    xp = round((totalScorePointsSC + totalScorePointsWC + totalScorePointsSP + totalScorePointsAP),0)

    return xp

def courseLeaderboard(currentCourse, context_dict):
    
    # Check if there are students in this course
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)

    if st_crs:
        if currentCourse:
            ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
                
            
            context_dict = generateLeaderboards(currentCourse)                
                       
        else:
            context_dict['course_Name'] = 'Not Selected'
        
    return context_dict
    
@login_required
def instructorCourseHome(request):
    
    context_dict, currentCourse = initialContextDict(request)
            
    context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
    context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
    context_dict['course_Name'] = currentCourse.courseName
    context_dict['courseId'] = currentCourse.courseID

    context_dict = courseLeaderboard(currentCourse, context_dict)
        
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)
