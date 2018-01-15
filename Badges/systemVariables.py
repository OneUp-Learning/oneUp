from Badges.enums import Event, ObjectTypes

from datetime import datetime
from Instructors.models import Challenges, Activities, Questions, Topics
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
objectTypeToObjectClass = {
    ObjectTypes.activity: Activities,
    ObjectTypes.challenge: Challenges,
    ObjectTypes.question: Questions,
    ObjectTypes.topic: Topics,
}
    
# This is where we evaluate the system variables in their appropriate
# context.
def calculate_system_variable(varIndex,course,student,objectType,objectID):
    print("VarIndex: " + str(varIndex))
    
    systemVar = SystemVariable.systemVariables[varIndex]
    functions = systemVar["functions"]
    if ObjectTypes.none in functions:
        return functions[ObjectTypes.none](course,student)
    else:
        if objectType not in functions:
            return "Error: no function defined to calculate this system variable for the specified object type (or no function defined to calculate it at all)!"
        object = objectTypeToObjectClass[objectType].objects.get(pk=objectID)
        return functions[objectType](course,student,object)

def getNumAttempts(course,student,challenge):
    from Students.models import StudentEventLog
    #Return the number of attempts (looking at only the startChallenge event trigger 801)
    numberOfAttempts = StudentEventLog.objects.filter(course = course, student = student, objectType = ObjectTypes.challenge, objectID = challenge.challengeID, event = Event.endChallenge).count()
    return numberOfAttempts

# Utility function used by other functions.  
def getTestScores(course,student,challenge):
    from Students.models import StudentChallenges
    return StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge)

# Utility function used by other functions.  
def getAllTestScores(course,challenge):
    from Students.models import StudentChallenges
    return StudentChallenges.objects.filter(courseID=course, challengeID=challenge)

def challengeScore(course,student,challenge):    
    #Return the test score from the fired event
    #Event enum is unspecified because it could be triggered on multiple occasions
    scores = getTestScores(course,student,challenge)
    if len(scores) == 0:
        return 0 
    return scores.latest('testScore').testScore #Ensure that only the most recent test score is returned

def activityScore(course,student,activity):
    from Students.models import StudentActivities
    scores = StudentActivities.objects.filter(activityID = activity, courseID = course, studentID = student)
    if len(scores) == 0:
        return 0
    return scores.latest('timestamp').activityScore

# Utility function used by other functions.
def getActivityScore(course, student ,activity):
    from Students.models import StudentActivities
    
    activities = StudentActivities.objects.filter(courseID=course, activityID=activity)
    scores = []
    
    for activity in activities:
        scores.append(activity.activityScore)
        
    return scores

def getMaxActivityScore(course, student, activity):
    '''Return the highest score of an activity per course'''
    
    scores = getActivityScore(course, activity)
    
    if scores:
        return int(max(scores))
    else:
        return 0
        
def getMinActivityScore(course, student, activity):
    '''Return the lowest score of an activity per course'''
    scores = getActivityScore(course, activity)
    
    if scores:
        return int(min(scores))
    else:
        return 0
    
def getAverageActivityScore(course,student, activity):
    '''Return the average score of an activity per course'''
    scores = getActivityScore(course, activity)
    
    if scores:
        return (float(sum(scores))/float(len(scores)))
    else:
        return 0
   
# the function accept studentChallengeID, not studentID 
def getPercentageOfCorrectAnswersPerChallengePerStudent(course,student, challenge):
    '''return percentage of correctly answered questions out of all the questions'''
    from Students.models import StudentChallengeQuestions
    from Instructors.models import ChallengesQuestions
    
    questionIds = []
    challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)
    for challenge_question in challenge_questions:
        questionIds.append(challenge_question.questionID)
    
    totalQuestions = len(questionIds)
    correctlyAnsweredQuestions = 0
    for question in questionIds:
        studentQuestion = StudentChallengeQuestions.objects.filter(studentChallengeID=student,questionID=question)
        
        if studentQuestion[0].questionTotal == studentQuestion[0].questionScore:
            correctlyAnsweredQuestions +=1
    
    if correctlyAnsweredQuestions != 0:
        percentage = ((float(correctlyAnsweredQuestions)/float(totalQuestions))*100)
        percentage = format(percentage,'.2f')
        return ((float(totalQuestions)/float(correctlyAnsweredQuestions))*100)
    else:
        return 0
def getAveragePercentageScore(course, student, challenge):
    ''' Utility function that returns the percentage of the average score
        a student has scored in a challenge
        ex. scores=[10, 5, 2], numberOfScores = 3, testTotal = 10, percentage = 56.7%
    '''
    allScores = getTestScores(course, student, challenge)
    percentage = 0
    if allScores.exists():
        testTotal = allScores[0]['testTotal']
        if testTotal == 0:
            return percentage
        scoreList = allScores.values_list('testScore', flat=True)
        numberOfScores = len(scoreList)
        percentage = round(((sum(scoreList)/numberOfScores)/testTotal) * 100, 1)
        logger.debug("Challenge Average Percentage: " + str(percentage) + "%")
        return percentage
    return percentage

def getHighestPercentageCorrect(course,student,challenge):
    #Return the actual correct percentage using the highest score from the fired event
    #Get the student score
    allScores = getTestScores(course,student,challenge)
    if allScores.exists():
        testScore = allScores.latest('testScore')
    else:
        return 0

    #Check if denominator is zero to avoid getting a DivideByZero error
    if float(testScore.testTotal) != 0:
        percentCorrect = (float(testScore.testScore)/float(testScore.testTotal)) * 100
    return percentCorrect

def getMaxTestScore(course,student,challenge):   
    #return the highest test score achieved out of the entire class for a challenge
    allTestScores = getAllTestScores(course,challenge)
    if len(allTestScores) == 0:
        return 0          
    highestTestScore = allTestScores.latest('testScore') #.latest() also gets the max for an integer value
    return highestTestScore

def getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge):
    #return the percentage of the higest text score
    # percentage of student's score (for the max scored attempt ) out of the max possible challenge score
 
    allScores = getTestScores(course,student,challenge)
    if allScores.exists():
        maxObject = allScores.latest('testScore')
        max = maxObject.testScore
        if float(maxObject.testTotal) != 0:
            return ((float(max)/float(maxObject.testTotal)) * 100)
        else:
            return 0
    else:
        return 0
    
def getAverageTestScore(course, students, challenge):
    #return the average score of the a challenge
    
    maxScores = 0.0
    
    for student in students:
        allScores = getTestScores(course,student,challenge)
        if allScores.exists():
            maxScore = allScores.latest('testScore').testScore
        
            maxScores += maxScore
        
    if len(students) != 0:
        return maxScores/float(len(students))
    else:
        return 0  
    
def getMinTestScore(course,student,challenge):
    #return the min test score achieved out of the entire class for a challenge
    allTestScores = getAllTestScores(course,challenge)
    if len(allTestScores) == 0:
        return 0    
    lowestTestScore = allTestScores.earliest('testScore') #.earliest() also gets the min for an integer value
    return lowestTestScore
    
def getDateOfFirstAttempt(course,student,challenge):
    from Students.models import StudentEventLog
    #return the oldest date from the event log with matching object ID (looking at only the endChallenge event trigger 802)
    attemptObjectsByDate = StudentEventLog.objects.filter(course = course, student = student,objectID = challenge,objectType = ObjectTypes.challenge, event = Event.endChallenge).order_by('-timestamp')
    if len(attemptObjectsByDate) > 0:
        return attemptObjectsByDate[0].timestamp
    else:
        return datetime(2000,1,1,0,0,0)

def totalTimeSpentOnChallenges(course,student):
    from Students.models import StudentChallenges
    # This calculates the time for both serious and warmup challenges
    #return the sum of delta times between StartChallenge and End Challenge events   
    challengeTimes = StudentChallenges.objects.filter(courseID = course,studentID = student).exclude(endTimestamp__isnull=True) #ensure that the challenge has an endTimestamp
    #Accumulate the elapsed time for all challenges in the database with matching student and course ID's
    #initialize totalTime as arbitrary datetime object in order to accumulate elapsed time
    totalTime = datetime(2000,1,1,0,0,0) #python throws Value Error if the date is too small, otherwise it would have been initialized to all 0's
    for challenge in challengeTimes:
        totalTime+=challenge.endTimestamp - challenge.startTimestamp
    totalTime -= datetime(2000,1,1,0,0,0) #subtract arbitrary value back out, in order to get the accurate elapsed time
    minutes = totalTime.total_seconds()/60 #convert total elapsed time to minutes
    return minutes

def totalTimeSpentOnQuestions(course,student):
    from Students.models import StudentEventLog
    #return the sum of delta times between Start Question and End Question events
    
    #TODO: Code assumes that question start times and question end times will come back in the same order.
    # This is not a fair assumption and this code should be rewritten to match the starts and ends together.
    # Also if a student starts a challenge and then abandons it, the counts will not be equal and then this code
    # will always return None for that student in that course.
    
    questionStartTimes = StudentEventLog.objects.filter(courseID = course,studentID = student, event = Event.startQuestion)
    questionEndTimes = StudentEventLog.objects.filter(courseID = course,studentID = student, event = Event.endQuestion)
    #assert that the two are of equal size

    if (questionStartTimes.count() == questionEndTimes.count()):
        #Accumulate the elapsed time for all questions in the database with matching student and course ID's
        #initialize totalTime as arbitrary datetime object in order to accumulate elapsed time
        totalTime = datetime(2000,1,1,0,0,0) #python throws Value Error if the date is too small, otherwise it would have been initialized to all 0's
        for (start,end) in zip(questionStartTimes, questionEndTimes):
            totalTime += end.timestamp - start.timestamp
        totalTime -= datetime(2000,1,1,0,0,0) #subtract arbitrary value back out, in order to get the accurate elapsed time
        minutes = totalTime.total_seconds()/60
        return minutes

def getConsecutiveDaysLoggedIn(course,student):
    from Students.models import StudentEventLog
    #Counter that sums every login event for a particular course with a new Day timestamp
    #return the counter

    #Cannot narrow this down to a login event type because the student may never "officially" log out
    #Instead we look at the day timestamp for any student-generated events
    #Must exclude participationNoted event because it is not generated by the student
    eventDates = StudentEventLog.objects.filter(student = student, course = course).values('timestamp').order_by('timestamp')
    studentEventDates = eventDates.exclude(event = Event.participationNoted)
    #Convert the days to integers to make them easier to compare
    dates = list(map(lambda d:d['timestamp'].toordinal(),studentEventDates))
    
    previous_day = 0   # This is probably Jan 1, 1 AD and shouldn't match.
    consecutive_days = 0
    for d in dates:
        if (d == previous_day):
            continue #if the days match, skip to the next event date
        elif(d - 1 == previous_day):
            consecutive_days += 1 #increment if the days are one off from each other
        else:
            consecutive_days = 0
        previous_day = d
    return consecutive_days

def getScorePercentage(course,student, challenge):
    '''Return of a challenge score per student'''
    from Students.models import StudentChallenges
    studentChallenges = StudentChallenges.objects.filter(courseID=course,studentID=student, challengeID=challenge)
    entirePoints = 0.0
    earnedPoints = 0.0
    for studentChallenge in studentChallenges:
        entirePoints = studentChallenge.testTotal
        earnedPoints = studentChallenge.testScore
                
    if entirePoints != 0.0:
        return ((float(earnedPoints) / float(entirePoints)) * 100)
    else:
        return 0

def getConsecutiveDaysWarmUpChallengesTaken30Percent(course,student): 
    from Students.models import StudentEventLog
    warmUpChallDates = []
    # filter all the ended challenge events
    eventObjects = StudentEventLog.objects.filter(student=student, course=course,event = Event.endChallenge)
    for event in eventObjects:
        if event.objectType == ObjectTypes.challenge: 
            # get a specific challenge by its ID
            chall = 0
            challenges = Challenges.objects.filter(courseID=course, challengeID=event.objectID)
            for challenge in challenges:
                chall = challenge  
            scorePecentage = getScorePercentage(course,student,event.objectID)
            # if the challenge is not graded then it's a warm up challenge and put in it in the list
            if not chall.isGraded and scorePecentage >= 30.0:
                # eventDate = str(event.timestamp)
                warmUpChallDates.append(event.timestamp.date())  
    # get today's date in utc            
    today = datetime.now(tz=timezone.utc).date()
    # if the student did not take any challenge return 0 as consecutiveDays
    if warmUpChallDates == []:
        return 0
    # if the student took only one challenge and the date is today return 1 otherwise 0
    elif len(warmUpChallDates) == 1:
        if warmUpChallDates[0] == today:
            return 1
        else:
            return 0   
    else:
        consecutiveDays = 1
        previousDate = warmUpChallDates[0]
        for date in warmUpChallDates[1:len(warmUpChallDates)-1]: 
            if(date - previousDate) == 1:
                consecutiveDays +=1
                previousDate = date
            elif (date - previousDate) == 0:
                continue
            else:
                consecutiveDays = 1
                previousDate = date   
        # if the last day the challenge taken is not today then return 0
        if warmUpChallDates[len(warmUpChallDates)-1] != today:
            consecutiveDays = 0
        return consecutiveDays
    
def getConsecutiveDaysWarmUpChallengesTaken75Percent(course,student): 
    from Students.models import StudentEventLog
    warmUpChallDates = []
    # filter all the ended challenge events
    eventObjects = StudentEventLog.objects.filter(student=student, course=course,event = Event.endChallenge)
    for event in eventObjects:
        if event.objectType == ObjectTypes.challenge: 
            # get a specific challenge by its ID
            chall = 0
            challenges = Challenges.objects.filter(courseID=course, challengeID=event.objectID)
            for challenge in challenges:
                chall = challenge  
            scorePecentage = getScorePercentage(course,student, event.objectID)
            # if the challenge is not graded then it's a warm up challenge and put in it in the list
            if not chall.isGraded and scorePecentage >= 75.0:
                # eventDate = str(event.timestamp)
                warmUpChallDates.append(event.timestamp.date())  
    # get today's date in utc            
    today = datetime.now(tz=timezone.utc).date()
    # if the student did not take any challenge return 0 as consecutiveDays
    if warmUpChallDates == []:
        return 0
    # if the student took only one challenge and the date is today return 1 otherwise 0
    elif len(warmUpChallDates) == 1:
        if warmUpChallDates[0] == today:
            return 1
        else:
            return 0   
    else:
        consecutiveDays = 1
        previousDate = warmUpChallDates[0]
        for date in warmUpChallDates[1:len(warmUpChallDates)-1]: 
            if(date - previousDate) == 1:
                consecutiveDays +=1
                previousDate = date
            elif (date - previousDate) == 0:
                continue
            else:
                consecutiveDays = 1
                previousDate = date   
        # if the last day the challenge taken is not today then return 0
        if warmUpChallDates[len(warmUpChallDates)-1] != today:
            consecutiveDays = 0
        return consecutiveDays    
    
def getActivitiesCompleted(course,student):
    from Students.models import StudentEventLog
    #Return the number of Participation Noted events
    numActivitiesCompleted = StudentEventLog.objects.filter(course = course,student = student,objectType = ObjectTypes.activity, event = Event.participationNoted).count()
    return numActivitiesCompleted

def getNumDaysSubmissionLateActivity(course, student , activity):
    '''Return the number of days an activity submitted after due date'''
    from Students.models import StudentActivities
    
    studentActivity = StudentActivities.objects.filter(courseID=course, studentID=student, activityID=activity)
    print("submission late " , getDaysDifferenceActity(activity,studentActivity[0]))
    return (-1 * getDaysDifferenceActity(activity,studentActivity[0]))
    
def getNumDaysSubmissionEarlyActivity(course, student , activity):
    '''Return the number of days an activity submitted before due date'''
    from Students.models import StudentActivities
    
    studentActivity = StudentActivities.objects.filter(courseID=course, studentID=student, activityID=activity)
    print("submission early " , getDaysDifferenceActity(activity,studentActivity[0]))
    return getDaysDifferenceActity(activity,studentActivity[0])

# utility function return defference in days between the submission and due date
def getDaysDifferenceActity(activity, studentActivity):
    deadline = activity.endTimestamp
    submission = studentActivity.timestamp
    print("Deadline ", deadline)
    print("submission", submission)
    return deadline - submission

def getDaysBetweenCurrentTimeAndDeadline(challenge):
    deadline = challenge.endTimestamp
    now = timezone.now()
    diff = deadline-now
    return diff.days

def calcNumDaysSubmissionEarly(course,student,challenge):
    return getDaysBetweenCurrentTimeAndDeadline(challenge)
        
def calcNumDaysSubmissionLate(course,student,challenge):
    return -1 * getDaysBetweenCurrentTimeAndDeadline(challenge)

def getConsecutiveClassesAttended(course,student):
    # This one we can't actually implement yet because we don't have the data.    
    return 0

def getConsecutiveWeeksOnLeaderboard(course,student):    
    import math
    from Students.models import StudentLeaderboardHistory

    # Assuming student has to be on leaderboard for atleast 7 days (AH)
    studentLog = StudentLeaderboardHistory.objects.filter(courseID = course, studentID = student, endTimestamp=None).values('startTimestamp')
    if not studentLog.exists():
        return 0
    studentLog = studentLog[0]
    startDate = studentLog['startTimestamp'].date()
    latestDate = datetime.now(tz=timezone.utc).date()
    delta = latestDate - startDate

    return math.trunc(delta.days/7)

def getNumberOfUniqueChallengesAttempted(course, student):
    ''' Get the number of serious challenges the student has taken.'''    
    challenges = Challenges.objects.filter(courseID=course, isGraded=True)
    attempted = 0
    for challenge in challenges:
        studentChallenges = getNumAttempts(course, student, challenge)
        if studentChallenges > 0:
            attempted += 1
    
    logger.debug("Serious Challenges Attempted: " + str(attempted))
    return attempted
    
def getTotalMinutesSpentOnWarmupChallenges(course, student):
    from Students.models import StudentChallenges
    
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    minutes = 0
    if not challenges.exists():
        return minutes
    for challenge in challenges:
        # Get student challenges where the endtimestamp is not null meaning they must complete the warmup challenge
        studentChallenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge.challengeID).exclude(endTimestamp__isnull=True).values('startTimestamp', 'endTimestamp')
        if len(studentChallenges) > 0:
            for studentChallenge in studentChallenges:
                endDate = studentChallenge['endTimestamp']
                startDate = studentChallenge['startTimestamp']
                delta = endDate - startDate
                minutes += (delta.seconds//60)%60
                
    logger.debug("Total minutes spent on warmup challenges: " + str(minutes))
    return minutes

def getConsecutiveScoresDifference(course, student, challenge):
    from Students.models import StudentChallenges, StudentEventLog
    difference = 0
    logger.debug(challenge)
    # Get the last challenge the student has taken whether it's a warmpup or serious challenge
    studentLastChallengeEvent = StudentEventLog.objects.filter(course = course, student = student, objectType = ObjectTypes.challenge, event = Event.endChallenge).exclude(objectID = challenge.challengeID).latest('timestamp')
    studentLastChallenge = StudentChallenges.objects.filter(courseID = course, studentID=student, challengeID = studentLastChallengeEvent.objectID)
    if studentLastChallenge.exists():
        # Get both challenges highest test score
        latestScore = challengeScore(course,student, studentLastChallengeEvent.objectID)
        previousScore = challengeScore(course, student, challenge.challengeID)
        logger.debug(latestScore)
        logger.debug(previousScore)
        
        difference = abs(previousScore - latestScore)
        logger.debug("Difference between last challenge score: " + str(difference))
        return difference
            
    return difference
            
def getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic(course, student, topic): 
    from Instructors.models import ChallengesTopics   
    challengesGreaterThan = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in challenges:
        # If topic is assigned to the warmup challenge then find percentage
        challengeTopics = ChallengesTopics.objects.filter(topicID=topic, challengeID = challenge.challengeID)
        if challengeTopics.exists():
            percentage = getHighestPercentageCorrect(course, student, challenge.challengeID)
            if percentage > 75.0:
                challengesGreaterThan += 1
    logger.debug("Number of unqiue warmup challenges with specific topic > 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan75Percent(course, student):    
    challengesGreaterThan = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in challenges:
        # Get the highest percentage correct from challenge. Also checks to see if student has taken that challenge
        percentage = getHighestPercentageCorrect(course, student, challenge.challengeID)
        if percentage > 75.0:
            challengesGreaterThan += 1
    logger.debug("Number of unqiue warmup challenges > 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan30Percent(course, student):    
    challengesGreaterThan = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in challenges:
        # Get the highest percentage correct from challenge. Also checks to see if student has taken that challenge
        percentage = getHighestPercentageCorrect(course, student, challenge.challengeID)
        if percentage > 30.0:
            challengesGreaterThan += 1
    logger.debug("Number of unqiue warmup challenges > 30%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def isWarmUpChallenge(course,student,challenge):
    return not challenge.isGraded

class SystemVariable():
    numAttempts = 901 # The total number of attempts that a student has given to a challenge
    score = 902 # The score for the challenge or activity
    percentageCorrect = 903 # The percentage of correct answers that a student has answered in an(single) attempt for a particular challenge
    maxTestScore = 904 # The maximum of the test scores of all the student's attempts for a particular challenge
    minTestScore = 905 # The minimum of the test scores of all the student's attempts for a particular challenge
    dateOfFirstAttempt = 906 # The date on which the student has attempted a particular challenge for the first time.
    timeSpentOnChallenges = 907 # Time spent on a particular challenge.
    timeSpentOnQuestions = 908 # Time spent on a particular question. 
    consecutiveDaysLoggedIn = 909 # The number of consecutive days a student logs in to the One Up website
    activitiesCompleted = 910 # The number of activities a student has completed for a particular course
    challengeId = 911 # The challenge ID if a badge is to be awarded for a specific challenge - CHECK the notes fop this!
    numDaysSubmissionEarlier = 912 #Number of days an assignment is submitted earlier
    numDaysSubmissionLate = 913 #Number of days an assignment is submitted late
    averageTestScore = 914  # Average Test Score
    consecutiveWeeksOnLeaderboard = 915 #Consecutive weeks on the leaderboard
    consecutiveClassesAttended = 916 #The number of consecutive classes a student has attended
    consecutiveDaysWarmUpChallengesTaken30Percent = 917 #Consecutive days warm up challenges at least 30% correct are taken
    consecutiveDaysWarmUpChallengesTaken75Percent = 918 #Consecutive days warm up challenges at least 75% correct are taken
    percentOfScoreOutOfMaxChallengeScore = 919  # percentage of student's score (for the max scored attempt ) out of the max possible challenge score
    uniqueChallengesAttempted = 920 # The number of unique challenges completed by the student
    uniqueWarmupChallengesGreaterThan30Percent = 921 # Number of warmup challenges with a score percentage greater than 30%
    uniqueWarmupChallengesGreaterThan75Percent = 922 # Number of warmup challenges with a score percentage greater than 75%
    uniqueWarmupChallengesGreaterThan75PercentForTopic = 923 # Number of warmup challenges with a score percentage greater than 75% for a particular topic
    totalMinutesSpentOnWarmupChallenges = 924 # Total minutes spent on warmup challenges only
    differenceFromLastChallengeScore = 925 # Score difference from last complete challenge/warmup challenge and a specific challenge
    minActivityScore = 926 # Lowest activity score of the course 
    maxActivityScore = 927 # highest activity score of the course 
    averageActivityScore = 928 # average activity score of the course 
    numDaysActivitySubmissionLate = 929 # Difference of days between submission and due date
    numDaysActivitySubmissionEarly =  930 # Difference of days between submission and due date
    percentageOfCorrectAnswersPerChallengePerStudent = 931 #percentage of correctly answered questions out of all the questions
    isWarmUp = 932 # is a warm-up challenge
    
    systemVariables = {
        numAttempts:{
            'index': numAttempts,
            'name':'numAttempts',
            'displayName':'Number of Attempts',
            'description':'The total number of attempts that a student has given to a challenge',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getNumAttempts
            }
        },
        score:{
            'index': score,
            'name':'score',
            'displayName':'Score',
            'description':'The score for the challenge or activity',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.activity: activityScore,
                ObjectTypes.challenge: challengeScore
            }    
        },
        percentageCorrect:{
            'index': percentageCorrect,
            'name':'percentageCorrect',
            'displayName':'Percentage Correct',
            'description':'The percentage of correct answers that a student has answered in an(single) attempt for a particular challenge',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getHighestPercentageCorrect
            }
        },
        maxTestScore:{
            'index': maxTestScore,
            'name':'maxTestScore',
            'displayName':'Maximum Challenge Score',
            'description':"The maximum of the test scores of all the student's attempts for a particular challenge",
            'eventsWhichCanChangeThis':[Event.challengeExpiration],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getMaxTestScore
            }
        },
        minTestScore:{
            'index': minTestScore,
            'name':'minTestScore',
            'displayName':'Minimum Challenge Score',
            'description':"The minimum of the test scores of all the student's attempts for a particular challenge",
            'eventsWhichCanChangeThis':[Event.challengeExpiration],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getMinTestScore
            }
        },
        dateOfFirstAttempt:{
            'index': dateOfFirstAttempt,
            'name':'dateOfFirstAttempt',
            'displayName':'Date of First Attempt',
            'description':'The date on which the student has attempted a particular challenge for the first time.',
            'eventsWhichCanChangeThis':[Event.startChallenge],
            'type':'date',
            'functions':{
                ObjectTypes.challenge: getDateOfFirstAttempt
            }
        },
        timeSpentOnChallenges:{
            'index': timeSpentOnChallenges,
            'name':'timeSpentOnChallenges',
            'displayName':'Time Spent On Warmup and Serious Challenges',
            'description':'Total time spent in the Challenges section for a particular course.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.none: totalTimeSpentOnChallenges
            }
        },
        timeSpentOnQuestions:{
            'index': timeSpentOnQuestions,
            'name':'timeSpentOnQuestions',
            'displayName':'Time Spent On Questions',
            'description':'Total time spent in the Questions section for a particular course.',
            'eventsWhichCanChangeThis':[Event.endQuestion], #I'm not sure this makes sense - Keith
            'type':'int',
            'functions':{
                ObjectTypes.none: totalTimeSpentOnQuestions
            }
        },
        consecutiveDaysLoggedIn:{
            'index':consecutiveDaysLoggedIn,
            'name':'consecutiveDaysLoggedIn',
            'displayName':'Consecutive Days Logged In',
            'description':'The number of consecutive days a student logs in to the One Up website.',
            'eventsWhichCanChangeThis':[Event.userLogin],
            'type':'int',
            'functions':{
                ObjectTypes.none: getConsecutiveDaysLoggedIn
            }
        },
        activitiesCompleted:{
            'index':activitiesCompleted,
            'name':'activitiesCompleted',
            'displayName':'Activities Completed',
            'description':'The number of activities a student has completed for a particular course.',
            'eventsWhichCanChangeThis':[Event.participationNoted],
            'type':'int',
            'functions':{
                ObjectTypes.none: getActivitiesCompleted
            }
        },
        minActivityScore:{
            'index':minActivityScore,
            'name':'minActivityScore',
            'displayName':'Lowest Activity Score',
            'description':'The lowest activity score for a particular course.',
            'eventsWhichCanChangeThis':[Event.participationNoted],
            'type':'int',
            'functions':{
                ObjectTypes.activity: getMinActivityScore
            }
        },
        maxActivityScore:{
            'index':maxActivityScore,
            'name':'maxActivityScore',
            'displayName':'Highest Activity Score',
            'description':'The highest activity score reached for a particular course.',
            'eventsWhichCanChangeThis':[Event.participationNoted],
            'type':'int',
            'functions':{
                ObjectTypes.activity: getMaxActivityScore
            }
        },
        averageActivityScore:{
            'index':averageActivityScore,
            'name':'averageActivityScore',
            'displayName':'Average Activity Score',
            'description':'The average activity score for a particular course.',
            'eventsWhichCanChangeThis':[Event.participationNoted],
            'type':'int',
            'functions':{
                ObjectTypes.activity: getAverageActivityScore
            }
        },
        numDaysSubmissionEarlier:{
            'index': numDaysSubmissionEarlier,
            'name':'numDaysSubmissionEarlier',
            'displayName':'Number of Days Submission Earlier',
            'description':'The number of days a submission is turned in earlier than the stated deadline',
            'eventsWhichCanChangeThis':[Event.endChallenge, Event.instructorAction, Event.studentUpload],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: calcNumDaysSubmissionEarly
            }
        },
        numDaysSubmissionLate:{
            'index': numDaysSubmissionLate,
            'name':'numDaysSubmissionLate',
            'displayName':'Number of Days Submission Late',
            'description':'The number of days a submission is turned in later than the stated deadline',
            'eventsWhichCanChangeThis':[Event.endChallenge, Event.instructorAction, Event.studentUpload],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: calcNumDaysSubmissionLate
            }
        },  
        numDaysActivitySubmissionLate:{
            'index': numDaysActivitySubmissionLate,
            'name':'numDaysActivitySubmissionLate',
            'displayName':'Number of Days Activity Submission Late',
            'description':'Difference of days between late activity submission and due date',
            'eventsWhichCanChangeThis':[Event.endChallenge, Event.instructorAction, Event.studentUpload],
            'type':'int',
            'functions':{
                ObjectTypes.activity: getNumDaysSubmissionLateActivity
            }
        },  
        numDaysActivitySubmissionEarly:{
            'index': numDaysActivitySubmissionEarly,
            'name':'numDaysActivitySubmissionEarly',
            'displayName':'Number of Days Activity Submission Early',
            'description':'Difference of days between early activity submission and due date',
            'eventsWhichCanChangeThis':[Event.endChallenge, Event.instructorAction, Event.studentUpload],
            'type':'int',
            'functions':{
                ObjectTypes.activity: getNumDaysSubmissionEarlyActivity
            }
        },                   
        consecutiveDaysWarmUpChallengesTaken30Percent:{
            'index': consecutiveDaysWarmUpChallengesTaken30Percent,
            'name':'consecutiveDaysWarmUpChallengesTaken30Percent',
            'displayName':'Consecutive Days Warm Up Challenges (at least 30% correct) Taken ',
            'description':'The number of consecutive days a student has taken Warm-up challenges (at least 30% correct).',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getConsecutiveDaysWarmUpChallengesTaken30Percent
            }
        },
        consecutiveDaysWarmUpChallengesTaken75Percent:{
            'index': consecutiveDaysWarmUpChallengesTaken75Percent,
            'name':'consecutiveDaysWarmUpChallengesTaken75Percent',
            'displayName':'Consecutive Days Warm Up Challenges (at least 75% correct) Taken ',
            'description':'The number of consecutive days a student has taken Warm-up challenges (at least 75% correct).',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getConsecutiveDaysWarmUpChallengesTaken75Percent
            }
        },
                       
        consecutiveWeeksOnLeaderboard:{
            'index': consecutiveWeeksOnLeaderboard,
            'name':'consecutiveWeeksOnLeaderboard',
            'displayName':'Consecutive Weeks on the Leaderboard',
            'description':'The number of consecutive weeks a student has been at the top 3 positions of the Leaderboard.',
            'eventsWhichCanChangeThis':[Event.leaderboardUpdate],
            'type':'int',
            'functions':{
                ObjectTypes.none: getConsecutiveWeeksOnLeaderboard
            }
        },
        consecutiveClassesAttended:{
            'index': consecutiveClassesAttended,
            'name':'consecutiveClassesAttended',
            'displayName':'Consecutive Classes Attended',
            'description':'The number of consecutive classes a student has attended.',
            'eventsWhichCanChangeThis':[Event.instructorAction],
            'type':'int',
            'functions':{
                ObjectTypes.none:getConsecutiveClassesAttended
            },
        }, 
        percentOfScoreOutOfMaxChallengeScore:{
            'index': percentOfScoreOutOfMaxChallengeScore,
            'name':'percentOfScoreOutOfMaxChallengeScore',
            'displayName':'Percent of student score out of max challenge score',
            'description':'Percentage of student score (for the max scored attempt) out of max challenge score.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getPercentOfScoreOutOfMaxChallengeScore
            },
        },                                             
        averageTestScore:{
            'index': averageTestScore,
            'name':'averageTestScore',
            'displayName':'Average Test Score',
            'description':'Average Test Score.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getAverageTestScore
            },
        },                        
        uniqueChallengesAttempted:{
            'index': uniqueChallengesAttempted,
            'name':'uniqueChallengesAttempted',
            'displayName':'Unique Challenges Attempted',
            'description':'The number of unique challenges attempted by the student.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueChallengesAttempted
            },
        },   
        uniqueWarmupChallengesGreaterThan30Percent:{
            'index': uniqueWarmupChallengesGreaterThan30Percent,
            'name':'uniqueWarmupChallengesGreaterThan30Percent',
            'displayName':'Warmup Challenges with Score > 30%',
            'description':'The number of warmup challenges with a score greater than 30%.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan30Percent
            },
        },
        uniqueWarmupChallengesGreaterThan75Percent:{
            'index': uniqueWarmupChallengesGreaterThan75Percent,
            'name':'uniqueWarmupChallengesGreaterThan75Percent',
            'displayName':'Warmup Challenges with Score > 75%',
            'description':'The number of warmup challenges with a score greater than 75%.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan75Percent
            },
        },
        uniqueWarmupChallengesGreaterThan75PercentForTopic:{
            'index': uniqueWarmupChallengesGreaterThan75PercentForTopic,
            'name':'uniqueWarmupChallengesGreaterThan75PercentForTopic',
            'displayName':'Warmup Challenges with Score > 75% for Specific Topic',
            'description':'The number of warmup challenges with a score greater than 75% for a specific topic.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic
            },
        },
        totalMinutesSpentOnWarmupChallenges:{
            'index': totalMinutesSpentOnWarmupChallenges,
            'name':'totalMinutesSpentOnWarmupChallenges',
            'displayName':'Total Minutes Spent on Warmup Challenges',
            'description':'The total minutes spent on all warmup challenges',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalMinutesSpentOnWarmupChallenges
            },
        },
        percentageOfCorrectAnswersPerChallengePerStudent:{
            'index': percentageOfCorrectAnswersPerChallengePerStudent,
            'name':'percentageOfCorrectAnswersPerChallengePerStudent',
            'displayName':'Percent of correctly answered questions',
            'description':'Percent of correctly answered questions out total number of questions.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getPercentageOfCorrectAnswersPerChallengePerStudent
            },
        },      
        differenceFromLastChallengeScore:{
            'index': differenceFromLastChallengeScore,
            'name':'differenceFromLastChallengeScore',
            'displayName':'Score Difference from Last Completed Challenge',
            'description':'Score difference from last complete challenge/warmup challenge and a specific challenge.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getConsecutiveScoresDifference
            },
        },
        isWarmUp:{
            'index': isWarmUp,
            'name': 'isWarmUp',
            'displayName': 'Is WarmUp Challenge',
            'description': 'True if the challenge in question is a warmup challenge, false if serious.',
            'eventsWhichCanChangeThis':[],
            'type':'boolean',
            'functions':{
                ObjectTypes.challenge:isWarmUpChallenge
            },
        },
    }
