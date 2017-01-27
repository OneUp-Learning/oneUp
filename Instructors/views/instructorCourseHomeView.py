'''
Created on Sep 10, 2016
Last Updated Sep 12, 2016

'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Announcements, Courses, Challenges
from Instructors.models import Skills, Courses, CoursesSkills 
from Badges.models import CourseConfigParams
from Badges.models import Badges, Courses
from Students.models import StudentConfigParams, StudentBadges,StudentChallenges,Student,StudentCourseSkills
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from _datetime import datetime, tzinfo
from time import time, strptime, struct_time
from time import strftime
from datetime import datetime, timedelta

import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

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
        
        ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
            
        if len(ccparamsList) > 0:
            ccparams = ccparamsList[0] 
            context_dict["badgesUsed"]=ccparams.badgesUsed
            context_dict["leaderboardUsed"]=ccparams.leaderboardUsed
            context_dict["classSkillsDisplayed"]=ccparams.classSkillsDisplayed
            context_dict["classRankingDisplayed "]=ccparams.classRankingDisplayed
            context_dict["numStudentToppersDisplayed"]=ccparams.numStudentToppersDisplayed
            context_dict["numStudentBestSkillsDisplayed"] = ccparams.numStudentBestSkillsDisplayed
            
        #Leaderboard Badges
#         StudentBadges(models.Model):
#     studentBadgeID = models.AutoField(primary_key=True)
#     studentID = models.ForeignKey(Student, verbose_name="the student", db_index=True)
#     badgeID = models.ForeignKey(Badges, verbose_name="the badge", db_index=True)
#     objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,assignment,etc. associated with a badge
#     timestamp = models.DateTimeField() ## Timestamp for badge assignment date
        badgeId = [] 
        studentBadgeID=[]
        studentID=[]
        badgeID=[]
        badgeName=[]
        badgeImage = []
        avatarImage =[]
        timestamp=[]
        N = 7
        

        date_N_days_ago = datetime.now() - timedelta(days=N)

        print ( datetime.now())
        print ("date_N_days_Ago")
        print (date_N_days_ago)
        
        
        #Displaying the list of challenges from database
        badges = StudentBadges.objects.all().order_by('-timestamp')
       
        for badge in badges:
            studentBadgeID.append(badge.studentBadgeID)
            studentID.append(badge.studentID)
            badgeID.append(badge.badgeID)
            badgeName.append(badge.badgeID.badgeName)
            badgeImage.append(badge.badgeID.badgeImage)
            avatarImage.append(badge.studentID.avatarImage)
#                 timestamp.append(badge.timestamp)
                          
            # The range part is the index numbers.
        context_dict['badgesInfo'] = zip(range(1,badges.count()),studentBadgeID,studentID,badgeID,badgeImage,avatarImage)
        print (badgeID)
        print(studentID)
        print (badgeName)
#         print (badge.timestamp)  
            ## Leaderboard Points
            
        ## Get the studentID for the course, then for each student in a loop get the total for all challenges for a student in that course
#         studentGradedChallenges = []
#         studentChallenges = StudentChallenges.objects.filter(studentID=studentID, courseID=currentCourse)
#         for st_challenge in studentChallenges:
#             if st_challenge.challengeID.isGraded:
#                 studentGradedChallenges.append(st_challenge)
#             for lp in studentGradedChallenges:
#                      
#                     studentChall_ID.append(lp.studentChallengeID) #pk
#                     chall_ID.append(lp.challengeID.challengeID) 
#                     total.append(lp.testTotal) 
#                     avatarImage.append(lp.studentID.avatarImage)           
#                 
#         context_dict['leaderpoints_range'] = zip(range(1,len(studentGradedChallenges)+1),studentChall_ID,chall_ID,total,avatarImage)
        # The range part is the index numbers.
         #Leaderboard Skills       
        ##################

        context_dict['skills'] = []
        courseID=[]
        cskills = CoursesSkills.objects.filter(courseID=currentCourse)
        for sk in cskills:

            skill = Skills.objects.get(skillID=sk.skillID.skillID)

            usersInfo=[]
            # TODO: Narrow down to only students in the current course                        
            user=Student.objects.all()
            for u in user: 
                skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=u,skillID = skill)
                skillPoints =0 ;
                    
                for sRecord in skillRecords:
                     skillPoints += sRecord.skillPoints
                if skillPoints > 0:
#                     skill_Points.append(skillPoints)
                    uSkillInfo = {'user':u.user,'skillPoints':skillPoints,'avatarImage':u.avatarImage} 
                    print("userSkillLst",uSkillInfo)
                    usersInfo.append(uSkillInfo)
            skillInfo = {'skillName':skill.skillName,'usersInfo':usersInfo}
#             context_dict['usersSkillsInfo'] = zip(range(1,len(usersSkillsInfo)),uSkillInfo)
            context_dict['skills'].append(skillInfo)

      
    # Leaderboard based on XP Points
    #Displaying the list of challenges from database
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True,  isVisible=True)
        num_challs = challenges.count()
        allgrades = []
        gradeTotal = []
        first_Name= []
        last_Name= []
        chall_Name= []
        

        #Displaying the list of students from database
        user = Student.objects.all()
        avatarImage =[]
        print ("[LBXP-Points]:",user)
        num_users = user.count()
        
        for i in range(0, num_users):  
            grade = []
            gradeMax = []
            number  = []
            numberMax  = []
            sc_user = []
            sc_chall = []
            
            for j in range(0, num_challs):  
                if StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]) :
                    
                    sChallenges = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j])
                    gradeID  = []
                    
                    for sc in sChallenges:
                        gradeID.append(int(sc.testScore))
                    numberMax.append(max(gradeID))
                    
                else:
                    numberMax.append(0)
                number = numberMax
            gradeTotal.append(("%0.2f" %sum(number)))
                
        for u in user:
            avatarImage.append(u.avatarImage)
        gradeTotal.sort(reverse=True)
#         context_dict['user_range'] = zip(range(1,user.count()+1),avatarImage, gradeTotal)
        context_dict['user_range'] = zip(range(1,ccparams.numStudentBestSkillsDisplayed+1),avatarImage, gradeTotal)
        
            
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)
