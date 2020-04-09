'''
Created on May 7, 2014

@author: Swapna
'''
from django.shortcuts import render
from django.utils import timezone
from Students.models import StudentChallenges, StudentProgressiveUnlocking
from Students.views.utils import studentInitialContextDict
from Instructors.models import Challenges , ChallengesQuestions, Topics, CoursesTopics, ChallengesTopics
from Instructors.views.utils import localizedDate
from Instructors.constants import unspecified_topic_name, unassigned_problems_challenge_name
from django.db.models import Q
from Badges.enums import ObjectTypes
from Badges.models import ProgressiveUnlocking
from datetime import datetime

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

    studentId = context_dict['student']

    if 'currentCourseID' in request.session:  
        if not context_dict['ccparams'].seriousChallengesGrouped:
            chall_ID = []      
            chall_Name = []         
            #chall_Difficulty = []
            chall_position = []
            # TODO: 
            # filtering
            #studentId = Student.objects.filter(user=request.user)
            currentTime = timezone.now() # TODO: Use current localtime
            if not str(user) == str(studentId):
                challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
            else:
                challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(hasStartTimestamp=False), Q(endTimestamp__gt=currentTime) | Q(hasEndTimestamp=False))
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
                        
                        if challenge.hasDueDate:
                            challDueDate.append(challenge.dueDate)
                        else:
                            challDueDate.append("")
                    
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
        else:
            #Displaying the list of challenges from database
            topic_ID = []      
            topic_Name = [] 
            topic_Pos = []     
            challenges_count = []   
            all_challenges_for_topic = []
            hasUnspecified_topic = False

            course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
            for ct in course_topics:
                
                tID = ct.topicID.topicID
                tName = Topics.objects.get(pk=tID).topicName
                if not tName == unspecified_topic_name:   # leave challenges with unspecified topic for last        
                    topic_ID.append(tID)
                    topic_Name.append(tName)
                    topic_Pos.append(ct.topicPos)
                    topic_challenges = studentChallengesForTopic(request, studentId, context_dict, ct.topicID, currentCourse) 
                    challenges_count.append(len(list(topic_challenges)))
                    all_challenges_for_topic.append(topic_challenges)
                else:
                    unspecified_topic = ct.topicID 
                    hasUnspecified_topic=True  
                
            # Add the challenges with unspecified topic at the end
            if hasUnspecified_topic:
                topic_ID.append(unspecified_topic.topicID)
                topic_Name.append("Miscellaneous")
                if topic_Pos: 
                    max_pos = max(topic_Pos)
                else:
                    max_pos = 0
                topic_Pos.append(max_pos+1) 
                topic_challenges = studentChallengesForTopic(request, studentId, context_dict, unspecified_topic, currentCourse)
                challenges_count.append(len(list(topic_challenges)))
                all_challenges_for_topic.append(topic_challenges)
                            
            context_dict['topic_range'] = sorted(list(zip(range(1,course_topics.count()+1),topic_ID,topic_Name,topic_Pos,challenges_count,all_challenges_for_topic)),key=lambda tup: tup[3])

    return render(request,'Students/ChallengesList.html', context_dict)

def studentChallengesForTopic(request, studentId, context_dict, topic, currentCourse):

    chall_ID = []  
    chall_Name = [] 
    chall_position = []

    grade = []
    gradeLast = []
    gradeFirst = []
    gradeMax = []
    gradeMin = []
    adjusmentReason = []
    challDueDate = []
    isUnlocked = []
    numberOfAttempts = []

    user = -1
    if request.user.is_authenticated:
        user = request.user.username
    
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    currentTime = timezone.now() # TODO: Use current localtime

    chall=Challenges.objects.filter(challengeName=unassigned_problems_challenge_name,courseID=currentCourse)
    for challID in chall:
        UnassignID = challID.challengeID  
    
    challenge_topics = ChallengesTopics.objects.filter(topicID=topic)
    
    if challenge_topics:           
        for challt in challenge_topics:
            if not str(user) == str(studentId):
                condition = Challenges.objects.filter(challengeID=challt.challengeID.challengeID, isGraded=True, courseID=currentCourse)
            else:
                condition = Challenges.objects.filter(challengeID=challt.challengeID.challengeID, isGraded=True, isVisible=True, courseID=currentCourse).filter(Q(startTimestamp__lt=currentTime) | Q(hasStartTimestamp=False), Q(endTimestamp__gt=currentTime) | Q(hasEndTimestamp=False))
            
            if condition:
                challenge = challt.challengeID
                if challenge.challengeID != UnassignID:
                    challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
                
                    if challQuestions:
                        if challenge.hasDueDate:
                            challDueDate.append(challenge.dueDate)
                        else:
                            challDueDate.append("")

                        chall_ID.append(challenge.challengeID) #pk
                        chall_Name.append(challenge.challengeName)
                        chall_position.append(challenge.challengePosition)
                                        
                        if StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge):
                            
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
                                numberOfAttempts.append(challenge.numberAttempts-len(sChallenges))
                            
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
    return sorted(list(zip(range(1,len(challenge_topics)+1),chall_ID,chall_Name,grade, numberOfAttempts,adjusmentReason, chall_position, challDueDate,isUnlocked)), key=lambda tup: tup[6])

