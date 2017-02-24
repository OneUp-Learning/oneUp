'''
Created on Feb 22, 2017

'''
from django.template import RequestContext
from django.shortcuts import render
from Students.models import StudentChallenges, Student
from Instructors.models import Challenges, Courses
from time import strftime
import datetime
from django.db.models import Q

from django.contrib.auth.decorators import login_required

@login_required
def CoursePerformance(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)
        context_dict['avatar'] = sID.avatarImage        
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0
        
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        print('current course:'+str(currentCourse))
        context_dict['course_Name'] = currentCourse.courseName
            
        chall_ID = []      
        chall_Name = []         
        chall_Difficulty = []
        
        studentId = Student.objects.filter(user=request.user)
        #Displaying the list of challenges from database
        
        # Default time is the time that is saved in the database when challenges are created with no dates assigned (AH)
        defaultTime = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
        currentTime = strftime("%Y-%m-%d %H:%M:%S")
        # Select if startTime is greater than(__gt) currentTime and 
        # if endTime is less than(__lt) currentTime (AH)
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))
        num_challs = challenges.count()
        
        grade = []
        gradeLast = []
        gradeFirst = []
        gradeMax = []
        gradeMin = []
        
        numberOfAttempts = []

        for j in range(0, num_challs):  
            if StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenges[j]) :
                
                sChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenges[j])
                latestSC = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                earliestSC =StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenges[j]).earliest('startTimestamp')
                
                gradeLast.append(str(latestSC.testScore) + " / " + str(latestSC.testTotal))
                gradeFirst.append(str(earliestSC.testScore) + " / " + str(earliestSC.testTotal))

                gradeID  = []
                
                numberOfAttempts.append(len(sChallenges))
                
                for sc in sChallenges:
                    gradeID.append(int(sc.testScore))

                gMax = (max(gradeID))
                gMin = (min(gradeID))
                
                gradeMax.append(str("%0.2f" % gMax) + " / " + str(latestSC.testTotal))
                gradeMin.append(str("%0.2f" % gMin) + " / " + str(latestSC.testTotal))
                
            else:
                gradeLast.append('Not Completed')
                gradeFirst.append('Not Completed')
                gradeMax.append('Not Completed')
                gradeMin.append('Not Completed')
                numberOfAttempts.append("0")

        if optionSelected == '1':
            grade = gradeLast
        elif optionSelected == '2':
            grade = gradeFirst
        elif optionSelected == '3':
            grade = gradeMax
        elif optionSelected == '4':
            grade = gradeMin
        else:
            grade = gradeLast
        
        
        if not challenges:
            print('No challenge')
            context_dict['no_challenge'] = 'Sorry!! there are no challenges associated with the course chosen..'
        else:
            for item in challenges:
                chall_ID.append(item.challengeID) #pk
                chall_Name.append(item.challengeName)
                chall_Difficulty.append(item.challengeDifficulty)
             
            # The range part is the index numbers.
            context_dict['challenge_range'] = zip(range(1,len(challenges)+1),chall_ID,chall_Name,chall_Difficulty,grade, numberOfAttempts)

    return render(request,'Students/ChallengesList.html', context_dict)