'''
Created on May 7, 2014

@author: Swapna
'''
from django.shortcuts import render
from Students.models import StudentChallenges
from Students.views.utils import studentInitialContextDict
from Instructors.models import Challenges , ChallengesQuestions
from Instructors.views.utils import utcDate
from Instructors.constants import default_time_str
from datetime import datetime
from django.db.models import Q



from django.contrib.auth.decorators import login_required

@login_required
def ChallengesList(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,currentCourse = studentInitialContextDict(request)
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:             
        chall_ID = []      
        chall_Name = []         
        #chall_Difficulty = []
        
        #studentId = Student.objects.filter(user=request.user)
        studentId = context_dict['student']
        #Displaying the list of challenges from database
        
        # Default time is the time that is saved in the database when challenges are created with no dates assigned (AH)
        defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        currentTime = utcDate()
        # Select if startTime is greater than(__gt) currentTime and 
        # if endTime is less than(__lt) currentTime (AH)
        
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))
        
        grade = []
        gradeLast = []
        gradeFirst = []
        gradeMax = []
        gradeMin = []
        
        numberOfAttempts = []
        
        

        for challenge in challenges:
            
            challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
            
            if challQuestions:
              
                if StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge ):
                    
                    sChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge)
                    latestSC = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')
                    earliestSC =StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge).earliest('startTimestamp')
                    
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
                print(item.challengeName)
                #chall_Difficulty.append(item.challengeDifficulty)
            
             
            # The range part is the index numbers.
            context_dict['challenge_range'] = zip(range(1,len(challenges)+1),chall_ID,chall_Name,grade, numberOfAttempts)

    return render(request,'Students/ChallengesList.html', context_dict)