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
                      
        context_dict = courseLeaderboard(currentCourse, context_dict)
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
        print("Xp")
        studentObkj = Student.objects.get(id=19)
        studentXP(studentObkj.id, currentCourse, False,False,False)
           
    #Trigger Student login event here so that it can be associated with a particular Course
    register_event(Event.userLogin, request, None, None)
    print("User Login event was registered for the student in the request")
    
    return render(request,'Students/StudentCourseHome.html', context_dict)           
        
        
        
def studentXP(studentId, course, warmup=False, serious=False, seriousPlusActivity=False):

    from Badges.models import CourseConfigParams
    from Instructors.models import Challenges, Activities, CoursesSkills, Skills
    from Students.models import StudentChallenges, StudentActivities, StudentCourseSkills
    
    xp = 0  
    xpWeightSP = 0
    xpWeightSChallenge = 0
    xpWeightWChallenge = 0
    xpWeightAPoints = 0
    ccparamsList = CourseConfigParams.objects.filter(courseID=course)
    if len(ccparamsList) >0:
        cparams = ccparamsList[0]
        xpWeightSP=cparams.xpWeightSP
        xpWeightSChallenge=cparams.xpWeightSChallenge
        xpWeightWChallenge=cparams.xpWeightWChallenge
        xpWeightAPoints=cparams.xpWeightAPoints
    
    print('ccp')
    print(xpWeightSP, xpWeightSChallenge, xpWeightWChallenge, xpWeightAPoints)
    # get the serious challenges for this course
    earnedScorePoints = 0 
    totalScorePoints = 0    
    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=True, isVisible=True)
    
    for challenge in courseChallenges:
        seriousChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)
    
        gradeID  = []                            
        for serious in seriousChallenge:
            gradeID.append(int(serious.getScoreWithBonus()))   # get the score + adjustment
                                
        if(gradeID):
            earnedScorePoints += max(gradeID)
            totalScorePoints += challenge.totalScore
    
         
    totalScorePointsSeriousChallenge = earnedScorePoints * xpWeightSChallenge / 100      # max grade for this challenge
    
    # get the warm up challenges for this course
    earnedScorePoints = 0 
    totalScorePoints = 0   
    
    courseChallenges = Challenges.objects.filter(courseID=course, isGraded=False, isVisible=True)
    for challenge in courseChallenges:
        warmupChallenge = StudentChallenges.objects.filter(studentID=studentId, courseID=course,challengeID=challenge)
    
        gradeID  = []                            
        for warmup in warmupChallenge:
            gradeID.append(int(warmup.testScore)) 
                               
        if(gradeID):
            earnedScorePoints += max(gradeID)
            totalScorePoints += challenge.totalScore
            
    totalScorePointsWarmupChallenge = earnedScorePoints * xpWeightWChallenge / 100      # max grade for this challenge
    # get the activity points for this course
    earnedActivityPoints = 0
    totalActivityPoints = 0
    
    courseActivities = Activities.objects.filter(courseID=course)
    for activity in courseActivities:
    
        sa = StudentActivities.objects.filter(studentID=studentId, courseID=course,activityID=activity)
    
        gradeID  = []                            
        for a in sa:
            gradeID.append(int(a.getScoreWithBonus())) 
                               
        if(gradeID):
            earnedActivityPoints += max(gradeID)
            totalActivityPoints += a.activityID.points
            
    totalScorePointsActivityPoints = earnedActivityPoints * xpWeightAPoints / 100
            
    # get the skill points for this course
    totalScoreSkillPoints = 0
    cskills = CoursesSkills.objects.filter(courseID=course)
    for sk in cskills:
        skill = Skills.objects.get(skillID=sk.skillID.skillID)
        
        sp = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId,skillID = skill)
        #print ("Skill Points Records", sp)
        gradeID = []
        
        for p in sp:
            gradeID.append(int(p.skillPoints))
            #print("skillPoints", p.skillPoints)
        if (gradeID):
            totalScoreSkillPoints = ((totalScoreSkillPoints + sum(gradeID,0)) * xpWeightSP / 100)
    
    if warmup==True:
        print("this is the warmup if")
        xp = round(totalScorePointsWarmupChallenge,1)
    elif serious == True:
        print("this is the serious if")
        xp = round(totalScorePointsSeriousChallenge,1)
    elif seriousPlusActivity == True:
        print("this is the sa if")
        xp = round((totalScorePointsSeriousChallenge  + totalScorePointsActivityPoints),1)
    else:
        print("this is the right if")
        xp = round((totalScorePointsSeriousChallenge + totalScorePointsWarmupChallenge  + totalScorePointsActivityPoints + totalScoreSkillPoints),1)
        
    print("Leaderboard created!", xp)
    
    
    