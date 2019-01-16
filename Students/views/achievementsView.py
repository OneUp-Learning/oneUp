'''
Created on May 27, 2015
Updated 06/09/2017

'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.models import Skills, Challenges, CoursesSkills, Activities, Milestones
from Students.models import StudentCourseSkills, StudentChallenges, StudentBadges, StudentRegisteredCourses,StudentActivities
from Badges.models import CourseConfigParams
from Students.views import classResults
from Students.views.utils import studentInitialContextDict
from Students.models import StudentConfigParams

from Badges.events import register_event
from Badges.enums import Event
from audioop import reverse

@login_required
def achievements(request):
 
    context_dict, currentCourse = studentInitialContextDict(request)
    
    context_dict["logged_in"]=request.user.is_authenticated


    studentId = context_dict['student']
    
    if "is_student" in context_dict:
        if context_dict["is_student"] == True:
            register_event(Event.visitedDashboard, request, studentId, None)
   
    st_crs = StudentRegisteredCourses.objects.get(studentID=studentId,courseID=currentCourse)
    context_dict['avatar'] = st_crs.avatarImage  
    context_dict['course_Bucks'] = str(st_crs.virtualCurrencyAmount)        

    curentStudentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=studentId) 
    context_dict['is_ClassAverage_Displayed'] = str(curentStudentConfigParams.displayClassAverage)
    context_dict['are_Badges_Displayed'] = str(curentStudentConfigParams.displayBadges)
    
    xpWeightSP=0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    xp = 0        
    ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
    if len(ccparamsList) >0:
        cparams = ccparamsList[0]           
        context_dict['badgesUsed']=str(cparams.badgesUsed)
        context_dict['levelingUsed']=str(cparams.levelingUsed)
        context_dict['leaderboardUsed']=str(cparams.leaderboardUsed)
        context_dict['classSkillsDisplayed']=str(cparams.classSkillsDisplayed)
        context_dict['virtualCurrencyUsed']=cparams.virtualCurrencyUsed
        
        xpWeightSP=cparams.xpWeightSP
        xpWeightSChallenge=cparams.xpWeightSChallenge
        xpWeightWChallenge=cparams.xpWeightWChallenge
        xpWeightAPoints=cparams.xpWeightAPoints
        print("Config Parameters::",xpWeightSP,xpWeightSChallenge,xpWeightWChallenge,xpWeightAPoints)
        
    #Begin Vendhan Changes        # XP Points Variable initialization
    # get the serious challenges for this course
    earnedPointsSeriousChallenges = 0  # total points earned from serious challenges, used for calculating student XP points
    chall_Name = []         
    score = []      # a list of the max points student earned for each serious challenge (if taken more than once) in this course
    total = []
    challavg = []

    # SERIOUS CHALLENGES  
    # We display information about all serious challenges for this course that should have been taken by the student,
    # not only for those taken by the student
    courseChallenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).order_by('challengePosition')
    for challenge in courseChallenges:
        sc = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse,challengeID=challenge)
        
        if not sc:          # if the challenge was not taken
            chall_Name.append(challenge.challengeName)    
            score.append(0)                           
            total.append(0)                      
            challavg.append(classResults.classAverChallengeScore(currentCourse,challenge.challengeID))
        else:    
            # find the max score for this challenge if there are several attempts                
            gradeID  = []
            gradeWithBonus = []   
            for s in sc:
                gradeID.append(int(s.getScore()))   # for serious challenges include also score adjustment and curve
                gradeWithBonus.append(int(s.getScoreWithBonus()))
                print(s.getScoreWithBonus()) 
                #s_testTotal = s.challengeID.totalScore
                s_testTotal = s.challengeID.getCombinedScore()
            maxC = max(gradeID)  
            maxB = max(gradeWithBonus)                
            earnedPointsSeriousChallenges += maxB
            score.append(maxC)
            chall_Name.append(challenge.challengeName)               
            total.append(s_testTotal)  
                
            challavg.append(classResults.classAverChallengeScore(currentCourse,challenge.challengeID))                       
     
    # weight points for serious challenges to be used in calculation of the XP Points   
    earnedPointsSeriousChallengesWeighted = earnedPointsSeriousChallenges * xpWeightSChallenge / 100    
    totalPointsSeriousChallenges =  sum(total)  
    
    context_dict['challenge_range'] = list(zip(range(1,len(courseChallenges)+1),chall_Name,score,total))
    context_dict['challengeWithAverage_range'] = list(zip(range(1,len(courseChallenges)+1),chall_Name,score,total,challavg))
     
 # WARM-UP CHALLENGES        
    chall_Name = []         
    total = []
    noOfAttempts = []
    warmUpMaxScore = []
    warmUpMinScore = []   
    warmUpSumScore = [] 
    warmUpSumPossibleScore = []   
    
    totalScorePointsWC = 0     # for calculating student XP points
    
    #GGM finding the order by taking for the challenges
    challengesOrderedByTaking = []
    allCourseChallenge = Challenges.objects.filter(courseID=currentCourse, isGraded=False, isVisible=True)
    for courseChallenge in allCourseChallenge:
        if courseChallenge.challengeName != "Unassigned Problems":
            studentWarmupChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse,challengeID=courseChallenge).order_by('-endTimestamp')
            if studentWarmupChallenge:
                challengesOrderedByTaking.append((courseChallenge,studentWarmupChallenge[0].endTimestamp))
     
           
    challengesOrderedByTaking = sorted(challengesOrderedByTaking, key=lambda tup: tup[1], reverse=True)
    
    courseChallenges = []
    for challengesOrdered in challengesOrderedByTaking:
        courseChallenges.append(challengesOrdered[0])
    
    for challenge in courseChallenges:
         wc = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse,challengeID=challenge).order_by('-endTimestamp')
         print(wc)
         
         if wc:          # if the challenge was taken           
            gradeID  = []
                                
            for w in wc:        # for each attempt of this challenge
                gradeID.append(int(w.testScore)) 
                print(w.testScore) 
                s_testTotal = w.challengeID.totalScore
            maxWC = max(gradeID)                
            totalScorePointsWC += maxWC
            
            warmUpMaxScore.append(maxWC)    
            warmUpMinScore.append(min(gradeID))
            warmUpSumScore.append(sum(gradeID)) # sum of the points for all attempts of this warm up challenge
            warmUpSumPossibleScore.append(s_testTotal*wc.count()) # max number of points   that can be earned by taking all attempts
            noOfAttempts.append(wc.count())                   
            
            chall_Name.append(challenge.challengeName)               
            total.append(s_testTotal)  
                         
    # weighting points for warm up challenges to be used in calculation of the XP Points   
    totalScorePointsWCWeighted = totalScorePointsWC * xpWeightWChallenge / 100    
    totalWCEarnedPoints = sum(warmUpSumScore)
    totalWCPossiblePoints = sum(warmUpSumPossibleScore)
    
    containerHeight = 100
    containerHeight += len(chall_Name) * 60
    
    context_dict['warmUpContainerHeight'] = containerHeight
    context_dict['studentWarmUpChallenges_range'] = list(zip(range(1,len(chall_Name)+1),chall_Name,total,noOfAttempts,warmUpMaxScore,warmUpMinScore))
    context_dict['totalWCEarnedPoints'] = totalWCEarnedPoints
    context_dict['totalWCPossiblePoints'] = totalWCPossiblePoints
            
 # ACTIVITY POINTS
    earnedActivityPoints = 0
    totalActivityPoints = 0
    courseActivities = Activities.objects.filter(courseID=currentCourse)
    for activity in courseActivities:
        sa = StudentActivities.objects.filter(studentID=studentId, courseID=currentCourse,activityID=activity)
        print("SA",sa)
        
        if sa:          # if activity was graded for this student            
            gradeID  = []
            gradeWithBonus = []             
            for a in sa:    # for each attempt of this activity
                gradeID.append(int(a.activityScore))  
                gradeWithBonus.append(int(a.getScoreWithBonus()))

            earnedActivityPoints += max(gradeWithBonus)
            totalActivityPoints += a.activityID.points
            print("totalActivityPoints; ", totalActivityPoints)                      

    # weighting points for activities to be used in calculation of the XP Points   
    earnedActivityPointsWeighted = earnedActivityPoints * xpWeightAPoints / 100
             
 # SKILL POINTS
    totalScorePointsSP = 0      # to be used in calculation of the XP Points     
    skill_Name = []                
    skill_Points = []
    skill_ClassAvg = []
    
    cskills = CoursesSkills.objects.filter(courseID=currentCourse)
    for sk in cskills:
        skill = Skills.objects.get(skillID=sk.skillID.skillID)
        
        sp = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId,skillID = skill)
        print ("Skill Points Records", sp)
        
        if not sp:          # if no points for this skill received
            skill_Name.append(skill.skillName)    
            skill_Points.append(0)                                                 
            skill_ClassAvg.append(classResults.skillClassAvg(skill.skillID, currentCourse))                       
        else:    
            # find the max score for this challenge if there are several attempts                
            gradeID  = []
            
            for p in sp:
                gradeID.append(int(p.skillPoints))
                print("skillPoints", p.skillPoints)   
             
            sumsp = sum(gradeID,0)                
            totalScorePointsSP = totalScorePointsSP + sumsp  
                
            skill_Points.append(sumsp)
            skill_Name.append(skill.skillName)
            skill_ClassAvg.append(classResults.skillClassAvg(skill.skillID, currentCourse))

    # weighting the total skill points to be used in calculation of the XP Points     
    print("totalScorePointsSP: ", totalScorePointsSP)              
    totalScorePointsSPWeighted = totalScorePointsSP * xpWeightSP / 100        
    
    context_dict['skill_range'] = list(zip(range(1,len(skill_Name)+1),skill_Name,skill_Points))
    context_dict['nondefskill_range'] = list(zip(range(1,len(skill_Name)+1),skill_Name,skill_Points))        
    context_dict['skillWithAverage_range'] = list(zip(range(1,len(skill_Name)+1),skill_Name,skill_ClassAvg))        
    
    #Sum up all weighted components to find the student's XP points
    xp = round((earnedPointsSeriousChallengesWeighted + totalScorePointsWCWeighted + totalScorePointsSPWeighted + earnedActivityPointsWeighted),0)
    context_dict['studentXP_range'] = xp
    context_dict['studentUngradedChallengesPPoints_range'] = totalScorePointsSPWeighted        
    #End Vendhan Changes
      
 # PROGRESS BAR

    # MILESTONES
    # this is the max points that the student can earn in this course
    totalMilestonePoints = 0
    milestones = Milestones.objects.filter(courseID=currentCourse)
    for stone in milestones:
        totalMilestonePoints += stone.points
    
    currentEarnedPoints = earnedPointsSeriousChallenges + earnedActivityPoints
    currentTotalPoints = totalPointsSeriousChallenges + totalActivityPoints
    missedPoints = currentTotalPoints - currentEarnedPoints 
    if not currentTotalPoints == 0:      
        projectedEarnedPoints = round(currentEarnedPoints * totalMilestonePoints/currentTotalPoints)
    else:
        projectedEarnedPoints = 0
    remainingPointsToEarn = totalMilestonePoints - currentTotalPoints
    
    print("totalMilestonePoints",totalMilestonePoints)
    print("currentEarnedPoints",currentEarnedPoints)
    print("currentTotalPoints",currentTotalPoints)
    print("missedPoints",missedPoints)
    print("projectedEarnedPoints",projectedEarnedPoints)
    print("remainingPointsToEarn",remainingPointsToEarn)
    
    context_dict['currentEarnedPoints'] = currentEarnedPoints
    context_dict['missedPoints'] = missedPoints
    context_dict['projectedEarnedPoints'] = projectedEarnedPoints
    context_dict['totalMilestonePoints'] = totalMilestonePoints
    context_dict['remainingPointsToEarn'] = remainingPointsToEarn
          
    
            
    # Extract Badges data for the current student
    badgeId = [] 
    badgeName = []
    badgeImage = []
    studentCourseBadges = []
        
    #Displaying the list of Badges from database
    studentBadges = StudentBadges.objects.filter(studentID=studentId).order_by('timestamp')
    for stud_badge in studentBadges:
        #print('stud_badge.badgeID.courseID'+str(stud_badge.badgeID.courseID))
        if stud_badge.badgeID.courseID == currentCourse:
            studentCourseBadges.append(stud_badge)

    for stud_badge in studentCourseBadges:
        #print('studentBadge: ') 
        badgeId.append(stud_badge.badgeID.badgeID)
        #print('studentBadge: '+str(stud_badge))
        badgeName.append(stud_badge.badgeID.badgeName)
        badgeImage.append(stud_badge.badgeID.badgeImage)
                    
         # The range part is the index numbers.
    #context_dict['badgesInfo'] = zip(range(1,studentBadges.count()+1),badgeId,badgeName,badgeImage)
    context_dict['badgesInfo'] = list(zip(range(1,len(studentCourseBadges)+1),badgeId,badgeName,badgeImage))
     
    return render(request,'Students/Achievements.html', context_dict)
