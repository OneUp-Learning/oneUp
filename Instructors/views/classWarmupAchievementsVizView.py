'''
Created on August 25, 2015

@author: Alex 
'''
from django.template import RequestContext
from django.shortcuts import render
import math
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Instructors.models import Courses, Challenges
from Students.models import Student, StudentChallenges, StudentCourseSkills
#from numpy import maximum

    
@login_required
def classWarmupAchievementsViz(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        
        first_Name = []      
        last_Name = []     
        chall_Name = [] 
        latest_log = []
        allgrades = []
        allgrades1 = []
        allgrades2 = []
        allgrades3 = []
        allgrades4 = []
        gradeTotal = []
        allChallengGrades = []
        #gradeMax  = []
        ChallengeCount = 0
        challengeGrade = []
        if 'ID' in request.GET:
            optionSelected = request.GET['ID']
            context_dict['ID'] = request.GET['ID']
        else:
            optionSelected = 0
                    
        #Displaying the list of challenges from database
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False)
        num_challs = challenges.count()
        num_challenges = challenges.count()
        
        #Displaying all the challenges (graded and non graded) from database
        allChallenges = Challenges.objects.filter(courseID=currentCourse)
        num_all_challs = allChallenges.count()
        
        #Displaying the list of students from database
        user = Student.objects.all()
        num_users = user.count()
        num_usercount = user.count()
        
        #Begin
        for t in range(0, num_challenges):
            skill_pointsUserTotal1 = []
            userScores = []
            maxTestScores = []
            minTestScores = []
            mediumTestScores = []
            userNames = []
            challNames = []            
            if StudentChallenges.objects.filter(courseID=currentCourse, challengeID = challenges[t]) :                    
                for i in range(0,num_usercount):
                    if StudentChallenges.objects.filter(studentID= user[i], courseID=currentCourse, challengeID = challenges[t]):
                        studentChall = StudentChallenges.objects.filter(studentID= user[i], courseID=currentCourse, challengeID = challenges[t]) 
                        latestChall = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[t]).latest('startTimestamp')
                        #print (str(studentChall[t]))
                        print (str(user[i]))
                        skill_pointsTotal1 = 0
                        print(str(latestChall.testScore))
                        challNames.append(challenges[t].challengeName)
                        userLatestScore = latestChall.testScore
                        #StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j])    
                        userScores.append(userLatestScore)
                        userGradeID  = []
                        for scr in studentChall:
                           userGradeID.append(int(scr.testScore))
                        
                        
                        maxTestScores.append(max(userGradeID))
                        minTestScores.append(min(userGradeID))
                        
                        mediumTestScores.append((max(userGradeID)+min(userGradeID))/2)
                        print('mediumTestScores: '+ str(mediumTestScores))
                        userNames.append(str(user[i].user.first_name+' '+user[i].user.last_name))
                        print (str(userNames))
                        studentSkills1 = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
                        if not studentSkills1:
                            print('No skills')
                            #skill_Points.append(0)
                        else:
                            for studentSkill in studentSkills1:                                                        
                                    #skill_Points1.append(studentSkill.skillPoints)
                                skill_pointsTotal1 +=studentSkill.skillPoints
                            skill_pointsUserTotal1.append(skill_pointsTotal1)     
                        allChallengGrades.append(zip(challNames, userNames, maxTestScores, mediumTestScores, minTestScores, skill_pointsUserTotal1 ))        
        #End;

        
        for i in range(0, num_users):     
            grade = []
            userGrade = []
            gradeLast = []
            gradeFirst = []
            gradeLatest = []
            gradeEarliest = []
            gradeMax = []
            gradeMin = []
            number  = []
            numberLast  = []
            numberFirst  = []
            numberLatest = []
            numberEarliest = []
            numberMax  = []
            numberMin  = []
            sc_user = []
            sc_user_name = []
            sc_chall = []
            challengeName = []
            userGradeMax = []
            userGradeMin = []
            nonGradedTotalTestScore = []
            userChallenges = []
            userGradeScore = 0
            skill_pointsUserTotal = []
            
            print ("userCount:"+str(i))
            print("User[i]"+str(user[i]))
            print("Num_challs " + str(num_challs))
            
            for j in range(0, num_challs):  
                if StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]) :
                    #print ("challenges[j]:"+str(challenges[j]))
                    challengeName.append(challenges[j])
                    sChallenges = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j])
                    latestSC = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                    earliestSC =StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).earliest('startTimestamp')
                    
                    gradeLast.append(latestSC.testScore)
                    gradeFirst.append(earliestSC.testScore)
                    numberLast.append(latestSC.testScore)
                    numberFirst.append(earliestSC.testScore)
                    
                    gradeLatest.append(latestSC.testScore)
                    gradeEarliest.append(earliestSC.testScore)
                    numberLatest.append(latestSC.testScore)
                    numberEarliest.append(earliestSC.testScore)
                    
                    sc_user.append(user[i])
                    user_Name = user[i].user.first_name+' '+user[i].user.last_name
                    sc_user_name.append(user_Name)
                    #print (str(user[i].user.first_name))
                    
                    sc_chall.append(challenges[j].challengeID)
                    gradeID  = []
                    
                    
                    for sc in sChallenges:
                        gradeID.append(int(sc.testScore))
                        
                        
                    gradeMax.append(max(gradeID))
                    gradeMin.append(min(gradeID))
                    userGradeMax.append(max(gradeID))
                    userGradeMin.append(min(gradeID))
                    numberMax.append(max(gradeID))
                    numberMin.append(min(gradeID))
                    
                    #Total Skill Points
                    skill_Points = []
                    skill_pointsTotal = 0
                    #skill_pointsUserTotal = []
                    studentSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
                    if not studentSkills:
                        print('No skills')
                        skill_Points.append(0)
                    else:
                        for studentSkill in studentSkills:                                                        
                            skill_Points.append(studentSkill.skillPoints)
                            skill_pointsTotal +=studentSkill.skillPoints
                    skill_pointsUserTotal.append(skill_pointsTotal) 
                    challengesNames = str(challenges[j].challengeName)
                    latestTestScore = str(latestSC.testScore)
                    print ("latestTestScore"+latestTestScore)
                    challengeGrade.append(zip(challengesNames,str(user_Name),latestTestScore,str(skill_pointsTotal)))      
                    ChallengeCount +=1;  
                    #print ("challengesNames: "+str(challengesNames))
                    #print ("user_Name:"+user_Name)
                    #print ("latestSC.testScore:"+str(latestSC.testScore))
                    #print ("skill_pointsUserTotal:"+str(skill_pointsUserTotal))   
                    #print("skill_pointsTotal:"+str(skill_pointsTotal))                 
                else:
                    gradeLast.append('-')
                    gradeFirst.append('-')
                    gradeMax.append('-')
                    gradeMin.append('-')
                    sc_user.append('-')
                    sc_chall.append('-')
                    
                    numberLast.append(0)
                    numberFirst.append(0)
                    numberMax.append(0)
                    numberMin.append(0)
                    
                    #challengeGrade.append(zip(range(1,user.count()+1),str(challenges[j].challengeName),str(user_Name),str(latestSC.testScore),str(skill_pointsUserTotal)))
            if optionSelected == '1':
                grade = gradeLast
                number = numberLast
                userGrade = gradeLast
            elif optionSelected == '2':
                grade = gradeFirst
                number = numberFirst
                userGrade = gradeFirst
            elif optionSelected == '3':
                grade = gradeMax
                number = numberMax
                userGrade = userGradeMax
            elif optionSelected == '4':
                grade = gradeMin
                number = numberMin
                userGrade = userGradeMin
            else:
                grade = gradeLast
                number = numberLast
                userGrade = gradeLast
            allgrades.append(zip(grade,sc_user,sc_chall))
            gradeTotal.append(int(sum(number)))
            #print (str(sc_user_name))
            #print ("challengeName[0]: "+str(challengeName[0]))
            
            #print("challengeName[1]:"+str(challengeName[1]))
            #for x in challengeName:
            #    print (x)
            #print("sc_user_name:"+str(sc_user_name[0]))
            #print("gradeLatest:"+str(gradeLatest[0]))
            #print("skill_pointsUserTotal:"+str(skill_pointsUserTotal))
            allgrades1.append(zip(challengeName,sc_user_name,gradeLatest,skill_pointsUserTotal)) 
            
            #print ("challengeName"+str(challengeName))
            #print (str(sc_user_name))
            #print (str(gradeLatest))
            #print (str(skill_pointsUserTotal))
            #print (next(zip(allgrades1)))
            #print("challengeGrade:" + str(challengeGrade) )
            
        for u in user:
            first_Name.append(u.user.first_name)
            last_Name.append(u.user.last_name)
            #print ("first_name:"+ str(first_Name))
        for c in challenges:
            chall_Name.append(c.challengeName)

        print (str(ChallengeCount))
        for x in challengeGrade:            
            print (list(x))
            print (len(challengeGrade))
        #for y in  allgrades1:
            #print (list(y))
            #print (len(allgrades1))   
        context_dict['challenge_range'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['user_range'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades, gradeTotal)
        
        context_dict['user_range1'] =zip(range(1,user.count()+1),allgrades1)
        # zip(range(1,user.count()+1),challengeGrade)
        #print  (str(user.count()+1))
        #print ("allChallengGrades.count"+str(allChallengGrades.count))
        chanllengeGradeCount = 0
        for l in allChallengGrades:
            chanllengeGradeCount+=1
        print ("chanllengeGradeCount"+str(chanllengeGradeCount))    
        context_dict['challengesRange'] = zip(range(0,chanllengeGradeCount),allChallengGrades)
        #zip(range(range(0,chanllengeGradeCount),allChallengGrades)
        context_dict['challengesCount'] = ChallengeCount
        
        #for t in range(0, num_all_challs):
            #print ("t:"+str(t))
            #if not StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[t]):
                #print ("t1: "+str(t))
            #else :
                #print ("t2: "+str(t)) 
                #userChallenges = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j])
                #latestSChall = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                #print (str(latestSChall.testScore))
                #userGradeScore += int(latestSChall.testScore)
                #print (str(userGradeScore)) 
                
    return render(request,'Instructors/ClassWarmupChallengesAchievementsViz.html', context_dict)
