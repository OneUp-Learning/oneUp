'''
Created on May 7, 2014

@author: Swapna
'''
from django.shortcuts import render
from Students.models import StudentChallenges, StudentProgressiveUnlocking
from Students.views.utils import studentInitialContextDict
from Instructors.models import Challenges , ChallengesQuestions
from Instructors.views.utils import utcDate
from Instructors.constants import default_time_str
from django.db.models import Q
from Badges.enums import ObjectTypes
from Badges.models import ProgressiveUnlocking


from django.contrib.auth.decorators import login_required

@login_required
def ChallengesList(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    
    
    context_dict,currentCourse = studentInitialContextDict(request)
    
    user = -1
    if request.user.is_authenticated:
        user = request.user.username
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:             
        chall_ID = []      
        chall_Name = []         
        #chall_Difficulty = []
        chall_position = []
        
        #studentId = Student.objects.filter(user=request.user)
        studentId = context_dict['student']
        #Displaying the list of challenges from database
        
        # Default time is the time that is saved in the database when challenges are created with no dates assigned (AH)
        defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        currentTime = utcDate()
        # Select if startTime is greater than(__gt) currentTime and 
        # if endTime is less than(__lt) currentTime (AH)
        
        if not str(user) == str(studentId):
            challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
        else:
            challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))
        
        grade = []
        gradeLast = []
        gradeFirst = []
        gradeMax = []
        gradeMin = []
        adjusmentReason = []
        challDueDate = []
        isUnlocked = []
        
        numberOfAttempts = []
        
        if not challenges:
            context_dict['no_challenge'] = 'Sorry!! there are no challenges associated with the course chosen..'
        else:

            for challenge in challenges:
                    
                challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
                
                if challQuestions:
                    
                    # if challenge.endTimestamp.strftime("%Y") < ("2900"):
                    #     challDueDate.append(challenge.endTimestamp)
                    # else:
                    #     challDueDate.append("")
                    challDueDate.append(challenge.dueDate)
                  
                    chall_ID.append(challenge.challengeID) #pk
                    chall_Name.append(challenge.challengeName)
                    chall_position.append(challenge.challengePosition)
                    
                    print(challenge.challengeName)
                    
                    if StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge ):
                        
                        sChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge)
                        latestSC = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')
                        earliestSC =StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge).earliest('startTimestamp')
                        
                        adjusmentReason.append(latestSC.adjustmentReason)
                        
                        gradeLast.append(str(latestSC.getScore()) + " / " + str(latestSC.challengeID.getCombinedScore()))
                        gradeFirst.append(str(earliestSC.getScore()) + " / " + str(earliestSC.challengeID.getCombinedScore()))
        
                        gradeID  = []
                        
                        if challenge.numberAttempts == 99999:
                            numberOfAttempts.append(challenge.numberAttempts)
                        else: 
                            diff = challenge.numberAttempts - len(sChallenges)
                            numberOfAttempts.append(diff)
                        
                        for sc in sChallenges:
                            gradeID.append(int(sc.getScore()))
        
                        gMax = (max(gradeID))
                        gMin = (min(gradeID))
                        
                        gradeMax.append(str("%0.2f" % gMax) + " / " + str(latestSC.challengeID.getCombinedScore()))
                        gradeMin.append(str("%0.2f" % gMin) + " / " + str(latestSC.challengeID.getCombinedScore()))
                        
                    else:
                        gradeLast.append('Not Completed')
                        gradeFirst.append('Not Completed')
                        gradeMax.append('Not Completed')
                        gradeMin.append('Not Completed')
                        numberOfAttempts.append(challenge.numberAttempts)
                        adjusmentReason.append("")
                
                # Progressive Unlocking
                studentPUnlocking = StudentProgressiveUnlocking.objects.filter(studentID=studentId,objectID=challenge.pk,objectType=ObjectTypes.challenge,courseID=currentCourse).first()
                if studentPUnlocking:
                    isUnlocked.append({'isFullfilled': studentPUnlocking.isFullfilled,'description': studentPUnlocking.pUnlockingRuleID.description})
                else:
                    isUnlocked.append({'isFullfilled': True,'description': ''})

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

        # The range part is the index numbers.
        context_dict['challenge_range'] = sorted(list(zip(range(1,len(challenges)+1),chall_ID,chall_Name,grade, numberOfAttempts,adjusmentReason, chall_position, challDueDate,isUnlocked)), key=lambda tup: tup[6])

    return render(request,'Students/ChallengesList.html', context_dict)