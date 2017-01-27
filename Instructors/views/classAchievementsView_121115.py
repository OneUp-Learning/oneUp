'''
Created on August 25, 2015

@author: Alex 
'''
from django.template import RequestContext
from django.shortcuts import render
import math
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Instructors.models import Courses, Challenges, CourseConfigParams
from Students.models import Student, StudentChallenges, StudentCourseSkills
#from numpy import maximum

    
@login_required
def classAchievements(request):
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
        
        curentCourseConfigParams = CourseConfigParams.objects.get(courseID=currentCourse)
        configParam_courseBucks = str(curentCourseConfigParams.courseBucks)
        configParam_isClassAverageDisplayed = str(curentCourseConfigParams.isClassAverageDisplayed)
        configParam_areBadgesDisplayed = str(curentCourseConfigParams.areBadgesDisplayed)
        print (configParam_courseBucks)
        context_dict['course_Bucks'] = configParam_courseBucks
        context_dict['is_ClassAverage_Displayed'] = str(configParam_isClassAverageDisplayed)
        context_dict['are_Badges_Displayed'] = str(configParam_areBadgesDisplayed)
        
        first_Name = []      
        last_Name = []    
        user_Name = [] 
        chall_Name = [] 
        latest_log = []
        allgrades1 = []
        allgrades2 = []
        allgrades3 = []
        allgrades4 = []
        gradeTotal1 = []
        gradeTotal2 = []
        gradeTotal3 = []
        gradeTotal4 = []
        #gradeMax  = []
        
        if 'ID' in request.GET:
            optionSelected = request.GET['ID']
            context_dict['ID'] = request.GET['ID']
        else:
            optionSelected = 0
                    
        #Displaying the list of challenges from database
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
        num_challs = challenges.count()
        
        #Displaying the list of students from database
        user = Student.objects.all()
        num_users = user.count()
        
        for i in range(0, num_users):  
            grade = []
            gradeLast = []
            gradeFirst = []
            gradeMax = []
            gradeMin = []
            number  = []
            numberLast  = []
            numberFirst  = []
            numberMax  = []
            numberMin  = []
            sc_user = []
            sc_chall = []
            nonGradedTotalTestScore = []
            challengeName = []
            
            for j in range(0, num_challs):                  
                if StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]) :
                    challengeName.append(challenges[j])
                    sChallenges = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j])
                    latestSC = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                    earliestSC =StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).earliest('startTimestamp')
                    
                    gradeLast.append(latestSC.testScore)
                    gradeFirst.append(earliestSC.testScore)
                    numberLast.append(latestSC.testScore)
                    numberFirst.append(earliestSC.testScore)
                    
                    sc_user.append(user[i])
                    
                    sc_chall.append(challenges[j].challengeName)
                    
                    gradeID  = []
                    
                    for sc in sChallenges:
                        gradeID.append(int(sc.testScore))
                        if not sc.challengeID.isGraded:
                            nonGradedTotalTestScore.append(sc.testScore)
                        
                    gradeMax.append(max(gradeID))
                    gradeMin.append(min(gradeID))
                    numberMax.append(max(gradeID))
                    numberMin.append(min(gradeID))
                    
                    #Total Skill Points
                    skill_Points = []
                    studentSkills = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], studentChallengeQuestionID__studentChallengeID__courseID=currentCourse)
                    if not studentSkills:
                        print('No skills')
                        skill_Points.append(0)
                    else:
                        for studentSkill in studentSkills:                                                        
                            skill_Points.append(studentSkill.skillPoints)
                            
                            
            else:
                    #gradeLast.append('-')
                    #gradeFirst.append('-')
                    #gradeMax.append('-')
                    #gradeMin.append('-')
                    #sc_user.append('-')
                    #sc_chall.append('-')
                    numberLast.append(0)
                    numberFirst.append(0)
                    numberMax.append(0)
                    numberMin.append(0)
            
             
            
            #print (sc_user)
            #print (sc_chall)
            
            #print (str(sc_user[0]))
            unique = []
            [unique.append(item) for item in sc_user if item not in unique]
            nameStr = unique
            #print (str(nameStr))
            #print (gradeLast)
            allgrades1.append(zip(sc_user,gradeLast,skill_Points,nonGradedTotalTestScore,challengeName))
            print (challengeName)
            print (nonGradedTotalTestScore)
            #gradeLast,sc_user,sc_chall))
            allgrades2.append(zip(sc_user,gradeFirst,skill_Points,nonGradedTotalTestScore,challengeName))
            #zip(gradeFirst,sc_user,sc_chall))
            allgrades3.append(zip(sc_user,gradeMax,skill_Points,nonGradedTotalTestScore,challengeName))
            #zip(gradeMax,sc_user,sc_chall))
            allgrades4.append(zip(sc_user,gradeMin,skill_Points,nonGradedTotalTestScore,challengeName))
            #zip(gradeMin,sc_user,sc_chall))
            gradeTotal1.append(int(sum(numberLast)))
            gradeTotal2.append(int(sum(numberFirst)))
            gradeTotal3.append(int(sum(numberMax)))
            gradeTotal4.append(int(sum(numberMin))) 
        for u in user:
            first_Name.append(u.user.first_name)
            last_Name.append(u.user.last_name)
            user_Name.append(u.user.first_name+' '+u.user.last_name)
        for c in challenges:
            chall_Name.append(c.challengeName)
        #print (str(chall_Name)) 
        #print (str(first_Name))
        #print (str(user_Name))
        #print(str(gradeTotal1))
        
        #print(str(allgrades1))
        #print(str(gradeTotal2))
        #print(str(allgrades2))
        #print(str(gradeTotal3))
        #print(str(allgrades3))
        #print(str(gradeTotal4))
        #print(str(allgrades4))
        context_dict['challenge_range1'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['challenge_range5'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['userNames5'] = zip(range(1,user.count()+1),user_Name)
        #print (str(user_Name))
        context_dict['user_range1'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades1,gradeLast, gradeTotal1)
        context_dict['user_range11'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades1,gradeLast, gradeTotal1)
        context_dict['user_range5'] = zip(range(1,user.count()+1),user_Name, gradeTotal1)
        context_dict['user_range55'] = zip(range(1,user.count()+1),user_Name, gradeTotal1)
        context_dict['challenge_range2'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['challenge_range6'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['user_range2'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades2,gradeFirst, gradeTotal2)
        context_dict['user_range22'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades2,gradeFirst, gradeTotal2)
        #context_dict['user_range6'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades2,gradeFirst, gradeTotal2)
        context_dict['userNames6'] = zip(range(1,user.count()+1),user_Name)
        context_dict['user_range6'] = zip(range(1,user.count()+1),user_Name, gradeTotal2)
        context_dict['user_range66'] = zip(range(1,user.count()+1),user_Name, gradeTotal2)
        context_dict['challenge_range3'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['challenge_range7'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['user_range3'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades3, gradeMax, gradeTotal3)
        context_dict['user_range33'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades3, gradeMax, gradeTotal3)
        context_dict['userNames7'] = zip(range(1,user.count()+1),user_Name)
        context_dict['user_range7'] = zip(range(1,user.count()+1),user_Name, gradeTotal3)
        context_dict['user_range77'] = zip(range(1,user.count()+1),user_Name, gradeTotal3)
        context_dict['challenge_range4'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['challenge_range8'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['user_range4'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades4, gradeMin, gradeTotal4)
        context_dict['user_range44'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades4, gradeMin, gradeTotal4)
        context_dict['userNames8'] = zip(range(1,user.count()+1),user_Name)
        context_dict['user_range8'] = zip(range(1,user.count()+1),user_Name, gradeTotal4)
        context_dict['user_range88'] = zip(range(1,user.count()+1),user_Name, gradeTotal4)
    return render(request,'Instructors/ClassAchievements.html', context_dict)
