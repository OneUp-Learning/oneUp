'''
Created on August 25, 2015

@author: Alex 
'''
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Challenges, Activities
from Instructors.views.utils import initialContextDict
from Students.models import StudentChallenges, StudentRegisteredCourses, StudentActivities
from oneUp.decorators import instructorsCheck  
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def classAchievements(request):
    context_dict, currentCourse = initialContextDict(request)
        
    first_Name = []      
    last_Name = []     
    chall_Name = [] 
    latest_log = []
    allgrades = []
    gradeTotal = []
    allActivityGrade = []
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0
                
    #Displaying the list of challenges from database
    challenges = list(Challenges.objects.filter(courseID=currentCourse, isGraded=True,  isVisible=True).order_by('endTimestamp'))
    num_challs = len(challenges)
    
    activities = Activities.objects.filter(courseID=currentCourse, isGraded=True).order_by('activityPosition')
    
    users = [] 
    #Displaying the list of students from the current class
    stud_course = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    for sc in stud_course:
        users.append(sc.studentID)
        
    for user in users:
        # Skip test students
        if user.isTestStudent:
            continue

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
        activityGradeStr = []
        
        for j in range(0, num_challs):  
            if StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j]) :
                
                sChallenges = StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j])
                latestSC = StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                earliestSC =StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j]).earliest('startTimestamp')
                
                gradeLast.append(latestSC.getScoreWithBonus())
                gradeFirst.append(earliestSC.getScoreWithBonus())
                numberLast.append(latestSC.getScoreWithBonus())
                numberFirst.append(earliestSC.getScoreWithBonus())
                
                sc_user.append(user)
                sc_chall.append(challenges[j].challengeID)
                gradeID  = []
                
                for sc in sChallenges:
                    gradeID.append(sc.getScoreWithBonus())
                gradeMax.append(("%0.2f" %max(gradeID)))
                gradeMin.append(("%0.2f" %min(gradeID)))
                numberMax.append(max(gradeID))
                numberMin.append(min(gradeID))
                
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
        
        totalActivityGrade = 0        
        for activity in activities:
            
            if StudentActivities.objects.filter(courseID=currentCourse, studentID=user, activityID=activity):
                activityGrade = StudentActivities.objects.get(courseID=currentCourse, studentID=user, activityID=activity).getScoreWithBonus()
                activityGradeStr.append(str(activityGrade))
                print(user, activityGrade)
            else:
                activityGrade = 0
                activityGradeStr.append("-")
            
            totalActivityGrade += activityGrade
        
        if optionSelected == '1':
            grade = gradeMax
            number = numberMax
        elif optionSelected == '2':
            grade = gradeMin
            number = numberMin
        elif optionSelected == '3':
            grade = gradeLast
            number = numberLast
        elif optionSelected == '4':
            grade = gradeFirst
            number = numberFirst
        else:
            grade = gradeMax
            number = numberMax
        
        total = sum(number) + totalActivityGrade
        allgrades.append(zip(grade,sc_user,sc_chall))
        gradeTotal.append(("%0.2f" %total))
        allActivityGrade.append(activityGradeStr)
        
    for u in users:
        # Skip test students
        if u.isTestStudent:
            continue

        first_Name.append(u.user.first_name)
        last_Name.append(u.user.last_name)
        
    for c in challenges:
        chall_Name.append(c.challengeName)
        
    for activity in activities:
        chall_Name.append(activity.activityName)

    context_dict['challenge_range'] = zip(range(1,num_challs+activities.count()+1),chall_Name)
    
    student_list = sorted(list(zip(range(1,len(users)+1),first_Name,last_Name,allgrades,allActivityGrade, gradeTotal)),key=lambda tup:tup[2])
    
    context_dict['user_range'] = student_list

    return render(request,'Instructors/ClassAchievements.html', context_dict)
