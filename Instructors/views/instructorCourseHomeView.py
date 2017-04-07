'''
Created on Sep 10, 2016
Last Updated Sep 12, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses, Challenges
from Instructors.models import Skills, CoursesSkills 
from Badges.models import CourseConfigParams
from Students.models import StudentBadges,StudentChallenges,Student,StudentCourseSkills, StudentRegisteredCourses
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from _datetime import datetime
from datetime import timedelta

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
            context_dict["numStudentsDisplayed"]=ccparams.numStudentsDisplayed
            context_dict["numStudentBestSkillsDisplayed"] = ccparams.numStudentBestSkillsDisplayed
            context_dict["numBadgesDisplayed"]=ccparams.numBadgesDisplayed
            
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

        #print ( datetime.now())
        #print ("date_N_days_Ago")
        #print (date_N_days_ago)
        
        
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
#                 timestamp.append(badge.timestamp)
                          
            # The range part is the index numbers.
        context_dict['badgesInfo'] = zip(range(1,ccparams.numBadgesDisplayed+1),studentBadgeID,studentID,badgeID,badgeImage,avatarImage)
        #print (badgeID)
        #print(studentID)
        #print (badgeName)
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
            
            st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)        
                                   
            for st_c in st_crs:
                u = st_c.studentID 
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

## Do the first list into a loop and slice and get the k elements
      
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
                
#         for u in user:                            #Why the avatars of all the students??????????
#             avatarImage.append(u.avatarImage)
        gradeTotal.sort(reverse=True)
#         context_dict['user_range'] = zip(range(1,user.count()+1),avatarImage, gradeTotal)
        context_dict['user_range'] = zip(range(1,ccparams.numStudentBestSkillsDisplayed+1),avatarImage, gradeTotal)
        
            
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)
