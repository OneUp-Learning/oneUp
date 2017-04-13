'''
Created on May 27, 2015

@author: dichevad
'''
from django.shortcuts import render
from datetime import datetime

from Instructors.models import Skills, Challenges, Courses, CoursesSkills, ChallengesQuestions
from Students.models import Student, StudentCourseSkills, StudentChallenges, StudentBadges, StudentRegisteredCourses
from Badges.models import CourseConfigParams
from Students.views import classResults
from Students.models import StudentConfigParams
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def achievements(request):

 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username     
    if 'userID' in request.GET:    
        stud = User.objects.filter(username=request.GET['userID'])
        context_dict["is_teacher"] = True
    else:
        context_dict["is_student"] = True
        stud = request.user

    studentId = Student.objects.filter(user=stud)
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        st_crs = StudentRegisteredCourses.objects.get(studentID=studentId,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage          
        
        print(str(currentCourse.courseName))
         
        # virtual currency has to be stored in Students - needs to change the model
        ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
        if len(ccparamsList) >0:
            cparams = ccparamsList[0]
            context_dict['badgesUsed']=str(cparams.badgesUsed)
            context_dict['levelingUsed']=str(cparams.levelingUsed)
            context_dict['leaderboardUsed']=str(cparams.leaderboardUsed)
            context_dict['classSkillsDisplayed']=str(cparams.classSkillsDisplayed)
            context_dict['virtualCurrencyUsed']=cparams.virtualCurrencyUsed
            print ('virtualCurrencyUsed   '+ str(cparams.virtualCurrencyUsed))

#         ccps = curentCourseConfigParamsObjects[0]
#         configParam_courseBucks = str(ccps.virtualCurrencyUsed)
        
        #configParam_courseBucks = 'True' 
               
        curentStudentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=studentId) 
        context_dict['is_ClassAverage_Displayed'] = str(curentStudentConfigParams.displayClassAverage)
        context_dict['are_Badges_Displayed'] = str(curentStudentConfigParams.displayBadges)
        #context_dict['course_Bucks'] = str(curentStudentConfigParams.courseBucks)
        
        stud_course = StudentRegisteredCourses.objects.get(courseID=currentCourse, studentID=studentId) 
        context_dict['course_Bucks'] = str(stud_course.virtualCurrencyAmount)

        
        #print ('courseBucks   ' + str(curentStudentConfigParams.courseBucks))
        
        #configParam_isClassAverageDisplayed = 'False'
        #configParam_areBadgesDisplayed = 'True'                  
        #print(str(configParam_isClassAverageDisplayed)) 
        #print (str(configParam_areBadgesDisplayed))
        #context_dict['course_Bucks'] = configParam_courseBucks
        #context_dict['is_ClassAverage_Displayed'] = str(configParam_isClassAverageDisplayed)
        #context_dict['are_Badges_Displayed'] = str(configParam_areBadgesDisplayed)
        #fieldNames = [i[0] for i in curentStudentConfigParams]
        #config_Params = str(curentStudentConfigParams).split(",")
        #print (fieldNames)
        #print (len(config_Params))
        #index = 0
        #for configItems in  config_Params:
        #    print(configItems[index], end=", ")     
        #    index +=1       
            #for configItem in configItems:
            #    print(str(configItem))
        #for item in curentStudentConfigParams:
         #   config_Params.append(item.IsClassAverageDisplayed)
        #context_dict['is_ClassAverageDisplayed'] = curentStudentConfigParams.IsClassAverageDisplayed
        #context_dict['are_BadgesDisplayed'] = curentStudentConfigParams.AreBadgesDisplayed
        
        # Extract Serious challenges data for the current student
        studentChall_ID = []
        chall_ID = []      
        chall_Name = []         
        chall_Difficulty = []
        dateTaken = []
        score = []
        total = []
         
        #Displaying the list of challenges that the student has taken from database
        
        
        # CHALLENGES    
        studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse)
                 
        #Filter only the GRADED challenges(serious challenges). container1 your points data
        studentGradedChallenges = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallenges.append(st_challenge)
                         
        if not studentGradedChallenges:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in studentGradedChallenges:
                print(str(studentGradedChallenges))
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                total.append(item.testTotal)            
            context_dict['gradedchallenge_range'] = zip(range(1,len(studentGradedChallenges)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)
        
         #Filter only the GRADED challenges (serious challenges).container1 your score data
        studentGradedChallengesScore = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesScore.append(st_challenge)
                         
        if not studentGradedChallengesScore:
            print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in studentGradedChallengesScore:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                total.append(item.testTotal)            
                # The range part is the index numbers.
            context_dict['gradedchallengescore_range'] = zip(range(1,len(studentGradedChallengesScore)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)

         #Filter only the GRADED challenges(serious challenges). container2 your points data
        studentGradedNonDefChallengesPoints = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedNonDefChallengesPoints.append(st_challenge)
                         
        if not studentGradedNonDefChallengesPoints:
            print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in studentGradedNonDefChallengesPoints:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                total.append(item.testTotal)            
                # The range part is the index numbers.
            context_dict['studentGradedNonDefChallengesPoints_range'] = zip(range(1,len(studentGradedNonDefChallengesPoints)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)
 
        #Filter only the GRADED challenges(serious challenges). container2 your points data
        challavg = []
       
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
        for challID in challenges:
            challavg.append(classResults.classAverChallengeScore(currentCourse,challID.challengeID, "average"))
            
        studentGradedNonDefChallengesAvgPoints = []        
        
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedNonDefChallengesAvgPoints.append(st_challenge)
                         
        if not studentGradedNonDefChallengesAvgPoints:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in studentGradedNonDefChallengesAvgPoints:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                total.append(item.testTotal)               
                # The range part is the index numbers.
                                
            context_dict['studentGradedNonDefChallengesAveragePoints_range'] = zip(range(1,len(studentGradedNonDefChallengesAvgPoints)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total, challavg)

        
         #Filter only the GRADED challenges (serious challenges).container1 your score data
        studentGradedNonDefChallengesScore = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedNonDefChallengesScore.append(st_challenge)
                         
        if not studentGradedNonDefChallengesScore:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in studentGradedNonDefChallengesScore:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                total.append(item.testTotal)           
                # The range part is the index numbers.
            context_dict['studentGradedNonDefChallengesScore_range'] = zip(range(1,len(studentGradedNonDefChallengesScore)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)

        #Score Points Start
        #Filter only the GRADED challenges (serious challenges).container1 your score data
        studentGradedChallengesScorePoints = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesScorePoints.append(st_challenge)
                         
        if not studentGradedChallengesScorePoints:
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            totalScorePoints = 0
            for item in studentGradedChallengesScorePoints:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                totalScorePoints = totalScorePoints + item.testScore
                total.append(item.testTotal)            
                # The range part is the index numbers.
            context_dict['studentGradedChallengesScorePoints_range'] = totalScorePoints
            
        #Score Points End
        
        #PointsEarned Start
         #Filter only the GRADED challenges (serious challenges).container1 your score data
        studentGradedChallengesPointsEarned = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesPointsEarned.append(st_challenge)
                         
        if not studentGradedChallengesPointsEarned:
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            PointsEarned = 0
            for item in studentGradedChallengesPointsEarned:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                PointsEarned = PointsEarned + item.testScore
                total.append(item.testTotal)        
                # The range part is the index numbers.     
                #print('PointsEarned:'+str(PointsEarned))       
            context_dict['studentGradedChallengesPointsEarned_range'] = PointsEarned
        #PointsEarned End
        
         #PointsEarned Start
         #Filter only the GRADED challenges (serious challenges).container1 your score data
        studentGradedChallengesPointsEarned = []
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesPointsEarned.append(st_challenge)
                         
        if not studentGradedChallengesPointsEarned:
            print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            PointsEarned = 0
            for item in studentGradedChallengesPointsEarned:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                PointsEarned = PointsEarned + item.testScore
                total.append(item.testTotal)            
            context_dict['studentGradedChallenges_range'] = PointsEarned
        #Remaining Challenges End  
   
        # WARM-UP CHALLENGES        
        # Extract Serious challenges data for the current student
        studentChall_ID = []
        chall_ID = []      
        chall_Name = []         
        chall_Difficulty = []
        dateTaken = []
        score = []
        total = []
        noOfAttempts = []
        challengesForAttempts = []
        noOfActualAttempts = []
        warmUpMaxScore = []
        warmUpMinScore = []
        warmUpChallenges = []        
        #Filter only the UNGRADED challenges(serious challenges)
        studentUngradedChallenges = []
        for st_challenge in studentChallenges:
            if not st_challenge.challengeID.isGraded:
               studentUngradedChallenges.append(st_challenge)
                                   
        # The range part is the index numbers.
        if not studentUngradedChallenges:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            
            for item in studentUngradedChallenges:
                 
                studentChall_ID.append(item.studentChallengeID)
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)                
                total.append(item.testTotal)
                warmUpChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = item.challengeID.challengeID )
                warmUpscore = []
                #noOfActualAttempts = 0
                for warmUpChall in warmUpChallenges:
                    if not warmUpChall.challengeID.isGraded:
                        warmUpscore.append(warmUpChall.testScore) 
                        #print("warmUpChall.Challenge"+str(warmUpChall.challengeID))
                        #print("warmUpChall.count"+str(warmUpChallenges.count()))
                        #print("warmUpChall.testscore"+str(warmUpChall.testScore))
                noOfActualAttempts.append(warmUpChallenges.count())   
                warmUpMaxScore.append(max(warmUpscore))    
                warmUpMinScore.append(min(warmUpscore))
                #print("chall_Name:"+str(chall_Name))
                #print("noOfActualAttempts:"+str(noOfActualAttempts))
                #print("warmUpMaxScore:"+str(warmUpMaxScore)) 
                #print("warmUpMinScore:"+str(warmUpMinScore))  
                challengesForAttempts = Challenges.objects.filter(challengeID=item.challengeID.challengeID)
                for challengeAttempt in challengesForAttempts:
                    noOfAttempts.append(challengeAttempt.numberAttempts) 
                    #print("challengeAttempt.numberAttempts:"+str(challengeAttempt.numberAttempts))    
                # The range part is the index numbers.
            context_dict['studentUngradedChallenges_range'] = zip(range(1,len(studentUngradedChallenges)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total)
            context_dict['studentWarmUpChallenges_range'] = zip(range(1,len(studentUngradedChallenges)+1),studentChall_ID,chall_ID,chall_Name,chall_Difficulty,dateTaken,score,total,noOfActualAttempts,warmUpMaxScore,warmUpMinScore)
        #Filter only the UNGRADED challenges for TotalPracticePoints
        studentUngradedChallengesPPoints = []
        for st_challenge in studentChallenges:
            if not st_challenge.challengeID.isGraded:
               studentUngradedChallengesPPoints.append(st_challenge)
                                   
        # The range part is the index numbers.
        if not studentUngradedChallengesPPoints:
            print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            totalScore = 0
            for item in studentUngradedChallengesPPoints:
                 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
                #print("studentUngradedChallengesPPoints: " + item.challengeID.challengeName)
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                dateTaken.append(strTime)
                score.append(item.testScore)
                totalScore = totalScore + item.testScore
                total.append(item.testTotal)
                             
                # The range part is the index numbers.
            context_dict['studentUngradedChallengesPPoints_range'] = totalScore
                         
       # Extract Skills data for the current student
       
       # First get all skills for this course
        skill_ID = []      
        skill_Name = []        
        
        cskills = CoursesSkills.objects.filter(courseID=currentCourse)
        for sk in cskills:
            skill_ID.append(sk.skillID.skillID) 
            skills = Skills.objects.filter(skillID=sk.skillID.skillID)
            for sname in skills:
                skill_Name.append(sname.skillName)
    
        skill_ID = []      
        skill_Name = []         
        skill_Points = []
        skillTotal_Points = []
        count = 0;
                    
        #Displaying the list of skills from database
        studentSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId, studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
        if not studentSkills:
            print('No skills')
            context_dict['no_skill'] = 'Sorry!! there are no skills associated with the course chosen..'
        else:
            
            for studentSkill in studentSkills:
                skill_ID.append(studentSkill.skillID) #pk
                skill_Name.append(studentSkill.skillID.skillName)
                skill_Points.append(studentSkill.skillPoints)
                
                # The range part is the index numbers.
            context_dict['skill_range'] = zip(range(1,studentSkills.count()+1),skill_ID,skill_Name,skill_Points)

        #Displaying the list of skills from database for Total Range
        defskillTotalCount = 0;
        studentSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId, studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
        if not studentSkills:
            #print('No skills')
            context_dict['no_skill'] = 'Sorry!! there are no skills associated with the course chosen..'
        else:
            for studentSkill in studentSkills:
                defskillTotalCount = 0;
                skill_ID.append(studentSkill.skillID) #pk
                skill_Name.append(studentSkill.skillID.skillName)
                skill_Points.append(studentSkill.skillPoints)
                defskillTotalCount = defskillTotalCount + studentSkill.skillPoints
                skillTotal_Points.append(defskillTotalCount)
               
                #print("defskillTotalCount"+str(defskillTotalCount))
                # The range part is the index numbers.
            context_dict['skillTotal_range'] = zip(range(1,studentSkills.count()+1),skill_ID,skill_Name,skill_Points,skillTotal_Points)
        
        #Displaying the list of nondefskills from database
        studentnondefSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId, studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
        if not studentnondefSkills:
            #print('No skills')
            context_dict['no_skill'] = 'Sorry!! there are no skills associated with the course chosen..'
        else:
            for studentSkill in studentnondefSkills:
                skill_ID.append(studentSkill.skillID) #pk
                skill_Name.append(studentSkill.skillID.skillName)
                skill_Points.append(studentSkill.skillPoints)
            #print("SkillId"+str(skill_ID))    
            #print("SkillNames"+str(skill_Name)) 
            #print("skillpoints"+str(skill_Points))
                # The range part is the index numbers.
            context_dict['nondefskill_range'] = zip(range(1,studentnondefSkills.count()+1),skill_ID,skill_Name,skill_Points)        
        
         #Displaying the list of nondefskills for avgskill points from database
        classskillavg =[]       
        skillavg_ID = []      
        skillavg_Name = []         
        skillavg_Points = []    
        studentnondefSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId, studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
        if not studentnondefSkills:
            #print('No skills')
            context_dict['no_skill'] = 'Sorry!! there are no skills associated with the course chosen..'
        else:
            for studentsSkill in studentnondefSkills:
                skillavg_ID.append(studentsSkill.skillID) #pk
                skillavg_Name.append(studentsSkill.skillID.skillName)
                skillavg_Points.append(studentsSkill.skillPoints)                
                classskillavg.append(classResults.skillClassAvg(studentsSkill.skillID, "challenge"))
                #print("SkillName"+str(skill_ID))
                #print("classskillavg"+str(classskillavg))
                # The range part is the index numbers.
            context_dict['nondefskillavgpoints_range'] = zip(range(1,studentnondefSkills.count()+1),skillavg_ID,skillavg_Name,classskillavg)        

        #Remaining Challenges Start
        #Filter only the GRADED challenges (serious challenges).p1 your Remaining Challenges data
        studentGradedRemainingChallenges = []
        RemainingChallengesPoints = 0
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedRemainingChallenges.append(st_challenge)
                         
        if not studentGradedRemainingChallenges:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            RemainingChallengesPoints = 0
            for item in studentGradedRemainingChallenges:
                #print("studentChallengeID"+str(item.studentChallengeID)) 
                #print("item.testScore"+str(item.testScore))
                #print("item.testTotal"+str(item.testTotal))
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                #print("strTime"+str(strTime))
                if not strTime:

                    RemainingChallengesPoints = RemainingChallengesPoints + item.testScore
                total.append(item.testTotal)
        
                # The range part is the index numbers.            
            context_dict['studentGradedRemainingChallenges_range'] = RemainingChallengesPoints
        #Remaining Challenges End 

        #Challenges Progress Points missed Start
        #Filter only the GRADED challenges (serious challenges).p1 your Remaining Challenges data
        studentGradedChallengesPointsMissed = []
        ChallengesPointsMissed = 0
        ChallengesTotalTestScore = 0
        ChallengesTotalPointsScore = 0

        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesPointsMissed.append(st_challenge)
                         
        if not studentGradedChallengesPointsMissed:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            ChallengesPointsMissed = 0
            for item in studentGradedChallengesPointsMissed:
 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                #print("strTime"+str(strTime))
                if strTime:
                    ChallengesTotalPointsScore = ChallengesTotalPointsScore + item.testScore
                    ChallengesTotalTestScore = ChallengesTotalTestScore + item.testTotal
            ChallengesPointsMissed = ChallengesTotalTestScore - ChallengesTotalPointsScore               
                # The range part is the index numbers.            
            context_dict['studentGradedChallengesPointsMissed_range'] = ChallengesPointsMissed
        #Challenges Progress Points missed End  

        #Challenges Progress Points projected Start
        #Filter only the GRADED challenges (serious challenges).p1 your Remaining Challenges data
        studentGradedChallengesPointsProjected = []
        ChallengesNotTakenTotalTestTotal = 0
        ChallengesPointsProjected = 0
        ChallengesTotalPointsScore = 0
        ChallengesTotalTestTotal = 0
        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesPointsProjected.append(st_challenge)
                         
        if not studentGradedChallengesPointsProjected:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            ChallengesNotTakenTotalTestTotal = 0
            ChallengesTotalTestTotal = 0
            ChallengesPointsProjected = 0
            ChallengesTotalPointsScore = 0
            for item in studentGradedChallengesPointsProjected:
                #print("studentChallengeID"+str(item.studentChallengeID)) 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                #print("strTime"+str(strTime))
                if strTime:
                    #print("item.testScore"+str(item.testScore))
                    #print("item.testTotal"+str(item.testTotal))
               
                    ChallengesTotalPointsScore = ChallengesTotalPointsScore + item.testScore
                    ChallengesTotalTestTotal = ChallengesTotalTestTotal + item.testTotal
                else:                    
                    ChallengesNotTakenTotalTestTotal = ChallengesNotTakenTotalTestTotal + item.testTotal 
                                    
            ChallengesPointsProjected = ChallengesTotalPointsScore + ((ChallengesTotalPointsScore / ChallengesTotalTestTotal) * ChallengesNotTakenTotalTestTotal)            

                # The range part is the index numbers.            
            context_dict['studentGradedChallengesPointsProjected_range'] = ChallengesPointsProjected
        #Challenges Progress Points Projected End 

       #Challenges Progress Max Points Start
        #Filter only the GRADED challenges (serious challenges).p1 your Max length Points Challenges data
        studentGradedChallengesMaxPoints = []
        ChallengesTotalTestTotal = 0

        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesMaxPoints.append(st_challenge)
                         
        if not studentGradedChallengesMaxPoints:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            ChallengesTotalTestTotal = 0            
            for item in studentGradedChallengesMaxPoints:
                #print("studentChallengeID"+str(item.studentChallengeID)) 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                #print("strTime"+str(strTime))
                ChallengesTotalTestTotal = ChallengesTotalTestTotal + item.testTotal 
            #print("ChallengesTotalTestTotal"+str(ChallengesTotalTestTotal))   
            
                # The range part is the index numbers.            
            context_dict['studentGradedChallengesMaxPoints_range'] = ChallengesTotalTestTotal
        #Challenges Progress Max Points End 
        
        #TotalSerious ChallengeQuestionsPoints Begin
        challengesNames = Challenges.objects.filter(courseID=currentCourse, isGraded = True)
        #print("challengesNames"+str(challengesNames))
        totalChallengeQuestionsScore = 0
        if not challengesNames:
            #print("No challenge")
            context_dict['no_challengeNames'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            for item in challengesNames:
                ChallengeQuestions = ChallengesQuestions.objects.filter(challengeID=item.challengeID)
                if not ChallengeQuestions:
                    print("No ChallengeQuestions")
                else:
                    for j in ChallengeQuestions:
                        totalChallengeQuestionsScore+= j.points 
        #print(str(totalChallengeQuestionsScore))
        context_dict['GradedChallengeQuestionsTotalPoints_range'] = totalChallengeQuestionsScore    
        #TotalSerious ChallengeQuestionsPoints End
        
         #Displaying the list of challenges that the student has taken from database
        
        challengesNames = Challenges.objects.filter(isGraded = True)
        #print("challengesNames"+str(challengesNames))
        challengesNames = Challenges.objects.filter(challengeName = 'QueuesSeriousCh1')
        #print("challengesNames"+str(challengesNames))
        # CHALLENGES    
        challengesQuestions = ChallengesQuestions.objects.all()
        #print("challengesQuestions"+str(challengesQuestions))
        #Challenges Progress Max Points Start
        #Filter only the GRADED challenges (serious challenges).p1 your Max length Points Challenges data
        gradedChallengesMaxPoints = []
        ChallengesTestTotal = 0

        for _challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                gradedChallengesMaxPoints.append(st_challenge)
                         
        if not gradedChallengesMaxPoints:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            ChallengesTestTotal = 0            
            for item in gradedChallengesMaxPoints:
                #print("studentChallengeID"+str(item.studentChallengeID)) 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                print("strTime"+str(strTime))
                ChallengesTestTotal = ChallengesTestTotal + item.testTotal 
            #print("ChallengesTotalTestTotal"+str(ChallengesTotalTestTotal))   
            
                # The range part is the index numbers.            
            context_dict['gradedChallengesMaxPoints_range'] = ChallengesTestTotal
        #Challenges Progress Max Points End 


       #Challenges Progress Tick Points Start
        #Filter only the GRADED challenges (serious challenges).p1 your Tick Points Challenges data
        studentGradedChallengesTickPoints = []
        ChallengesTotalTestScore = 0

        for st_challenge in studentChallenges:
            if st_challenge.challengeID.isGraded:
                studentGradedChallengesTickPoints.append(st_challenge)
                         
        if not studentGradedChallengesTickPoints:
            #print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! you did not take any challenges in the selected course..'
        else:
            ChallengesTotalTestScore = 0            
            for item in studentGradedChallengesTickPoints:
                #print("studentChallengeID"+str(item.studentChallengeID)) 
                studentChall_ID.append(item.studentChallengeID) #pk
                chall_ID.append(item.challengeID.challengeID) 
                chall_Name.append(item.challengeID.challengeName)
               
                chall_Difficulty.append(item.challengeID.challengeDifficulty)
                strTime = datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p" )
                #print("strTime"+str(strTime))
                ChallengesTotalTestScore = ChallengesTotalTestScore + item.testScore   
            
                # The range part is the index numbers.            
            context_dict['studentGradedChallengesTickPoints_range'] = ChallengesTotalTestScore
        #Challenges Progress Tick Points End 
  
    
    #Total Skill score points  
        skillTotal_ID = []      
        skillTotal_Name = []         
        #skillTotal_Points = []    
        classskillTotal = []
        skilltotalpoints = 0;
        studentnondefSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId, studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
        if not studentnondefSkills:
            #print('No skills')
            context_dict['no_skill'] = 'Sorry!! there are no skills associated with the course chosen..'
        else:
            for studentsSkill in studentnondefSkills:
                skilltotalpoints = 0;
                skillTotal_ID.append(studentsSkill.skillID) #pk
                skillTotal_Name.append(studentsSkill.skillID.skillName)
                skillTotal_Points.append(studentsSkill.skillPoints)                
                skilltotalpoints+=studentsSkill.skillPoints
                skillTotal_Points.append(skilltotalpoints)
           
                # The range part is the index numbers.
            context_dict['nondefskillTotalpoints_range'] = zip(range(1,studentnondefSkills.count()+1),skillTotal_ID,skillTotal_Name,skillTotal_Points)        
              
                
        # Extract Badges data for the current student
        badgeId = [] 
        badgeName = []
        badgeImage = []
        studentCourseBadges = []
            
            #Displaying the list of Badges from database
        studentBadges = StudentBadges.objects.filter(studentID=studentId)
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
        context_dict['badgesInfo'] = zip(range(1,len(studentCourseBadges)+1),badgeId,badgeName,badgeImage)

        
    return render(request,'Students/Achievements.html', context_dict)
