'''
Created on Sep 14, 2016

'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Courses,Skills,CoursesSkills, Challenges
from Badges.models import CourseConfigParams
from Students.models import StudentConfigParams,Student,StudentBadges,StudentChallenges,StudentCourseSkills
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
# from Instructors.views.preferencesView import createContextForUpcommingChallengesList

from Badges.enums import Event
from Badges.events import register_event
from _datetime import datetime, tzinfo
from time import time, strptime, struct_time
from time import strftime
from datetime import datetime, timedelta


def StudentCourseHome(request):
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)
        print(sID)

    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']
    
    if request.GET:
        request.session['currentCourseID'] = request.GET['courseID']
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
        context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
        context_dict['course_Name'] = currentCourse.courseName
        context_dict['avatar'] = sID.avatarImage
        ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
        if len(ccparamsList) >0:
            cparams = ccparamsList[0]
            context_dict["badgesUsed"]=cparams.badgesUsed
            context_dict["levelingUsed"]=cparams.levelingUsed
            context_dict["leaderboardUsed"]=cparams.leaderboardUsed
            context_dict["classSkillsDisplayed"]=cparams.classSkillsDisplayed
            context_dict["numStudentToppersDisplayed"]=cparams.numStudentToppersDisplayed
            context_dict["numStudentBestSkillsDisplayed"]=cparams.numStudentBestSkillsDisplayed
            
        scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=sID)    
        if len(scparamsList) > 0:
            scparams = scparamsList[0]
            context_dict["displayBadges"]=scparams.displayBadges
            context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
            context_dict["displayClassAverage"]=scparams.displayClassAverage
            context_dict["displayClassSkills"]=scparams.displayClassSkills
        
        
        # Leaderboard based on XP Points
        #Displaying the list of challenges from database
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True,  isVisible=True)
        num_challs = challenges.count()
        allgrades = []
        gradeTotal = []
        first_Name=[]
        last_Name=[]
        chall_Name=[]
        

        #Displaying the list of students from database
        user = Student.objects.filter()
        avatarImage =[]
        print (user)
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
        context_dict['user_range'] = zip(range(1,cparams.numStudentBestSkillsDisplayed+1),avatarImage, gradeTotal)
         
         #Leaderboard Skills       
        context_dict['skills'] = []
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
        # Add needed information
     
        studentBadgeID=[]
        studentID=[]
        badgeID=[]
        badgeName=[]
        badgeImage = []
        avatarImage =[]
        N = 7

        date_N_days_ago = datetime.now() - timedelta(days=N)

        print ( datetime.now())
        print ("date_N_days_Ago")
        print (date_N_days_ago)                
        #Displaying the list of badges from database
        badges = StudentBadges.objects.all().order_by('-timestamp')
        print(badges)
        for badge in badges:
                studentBadgeID.append(badge.studentBadgeID)
                studentID.append(badge.studentID)
                badgeID.append(badge.badgeID)
                badgeName.append(badge.badgeID.badgeName)
                badgeImage.append(badge.badgeID.badgeImage)
                avatarImage.append(badge.studentID.avatarImage)
    #                 timestamp.append(badge.timestamp)
        print (badgeID)
        print(studentID)
        print (badgeName)
                # The range part is the index numbers.
        context_dict['badgesInfo'] = zip(range(1,badges.count()+1),studentBadgeID,studentID,badgeID,badgeImage,avatarImage)
        print (badgeID)
        print (studentID)
        print (badgeName)
        
    #Trigger Student login event here so that it can be associated with a particular Course
    register_event(Event.userLogin, request, None, None)
    print("User Login event was registered for the student in the request")
    
    return render(request,'Students/StudentCourseHome.html', context_dict)