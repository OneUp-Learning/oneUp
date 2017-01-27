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
from Students.models import Student, StudentChallenges
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
        
        first_Name = []      
        last_Name = []     
        chall_Name = [] 
        latest_log = []
        allgrades = []
        gradeTotal = []
        #gradeMax  = []
        
        if 'ID' in request.GET:
            optionSelected = request.GET['ID']
            context_dict['ID'] = request.GET['ID']
        else:
            optionSelected = 0
                    
        #Displaying the list of challenges from database
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True,  isVisible=True)
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
            
            for j in range(0, num_challs):  
                if StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]) :
                    
                    sChallenges = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j])
                    latestSC = StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                    earliestSC =StudentChallenges.objects.filter(studentID=user[i], courseID=currentCourse, challengeID = challenges[j]).earliest('startTimestamp')
                    
                    gradeLast.append(latestSC.testScore)
                    gradeFirst.append(earliestSC.testScore)
                    numberLast.append(latestSC.testScore)
                    numberFirst.append(earliestSC.testScore)
                    
                    sc_user.append(user[i])
                    sc_chall.append(challenges[j].challengeID)
                    gradeID  = []
                    
                    for sc in sChallenges:
                        gradeID.append(int(sc.testScore))
                        
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
            
            if optionSelected == '1':
                grade = gradeLast
                number = numberLast
            elif optionSelected == '2':
                grade = gradeFirst
                number = numberFirst
            elif optionSelected == '3':
                grade = gradeMax
                number = numberMax
            elif optionSelected == '4':
                grade = gradeMin
                number = numberMin
            else:
                grade = gradeLast
                number = numberLast
            
            allgrades.append(zip(grade,sc_user,sc_chall))
            gradeTotal.append(("%0.2f" %sum(number)))
             
        for u in user:
            first_Name.append(u.user.first_name)
            last_Name.append(u.user.last_name)
        
        for c in challenges:
            chall_Name.append(c.challengeName)

        context_dict['challenge_range'] = zip(range(1,challenges.count()+1),chall_Name)
        context_dict['user_range'] = zip(range(1,user.count()+1),first_Name,last_Name,allgrades, gradeTotal)

    return render(request,'Instructors/ClassAchievements.html', context_dict)
