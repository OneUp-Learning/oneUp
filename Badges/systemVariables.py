from Badges.enums import Event, ObjectTypes
from Students.models import StudentEventLog, StudentChallenges,\
    StudentActivities
from datetime import datetime
from Instructors.models import Challenges, Activities, Questions
from django.utils import timezone

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
    consecutiveDaysWarmUpChallengesTaken = 914  #Consecutive days warm up challenges are taken
    consecutiveWeeksOnLeaderboard = 915 #Consecutive weeks on the leaderboard
    consecutiveClassesAttended = 916 #The number of consecutive classes a student has attended
    
    systemVariables = {
        numAttempts:{
            'index': numAttempts,
            'name':'numAttempts',
            'displayName':'Number of Attempts',
            'description':'The total number of attempts that a student has given to a challenge',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'functions':{
                ObjectTypes.challenge: numAttempts
            }
        },
        score:{
            'index': score,
            'name':'score',
            'displayName':'Challenge or Activity Score',
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
                ObjectTypes.challenge: percentageCorrect
            }
        },
        maxTestScore:{
            'index': maxTestScore,
            'name':'maxTestScore',
            'displayName':'Maximum Challenge Score',
            'description':"The maximum of the test scores of all the student's attempts for a particular challenge",
            'eventsWhichCanChangeThis':[Event.challengeExpiration],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.challenge],
        },
        minTestScore:{
            'index': minTestScore,
            'name':'minTestScore',
            'displayName':'Minimum Challenge Score',
            'description':"The minimum of the test scores of all the student's attempts for a particular challenge",
            'eventsWhichCanChangeThis':[Event.challengeExpiration],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.challenge],
        },
        dateOfFirstAttempt:{
            'index': dateOfFirstAttempt,
            'name':'dateOfFirstAttempt',
            'displayName':'Date of First Attempt',
            'description':'The date on which the student has attempted a particular challenge for the first time.',
            'eventsWhichCanChangeThis':[Event.startChallenge],
            'type':'date',
            'objectsDefinedFor':[ObjectTypes.challenge],
        },
        timeSpentOnChallenges:{
            'index': timeSpentOnChallenges,
            'name':'timeSpentOnChallenges',
            'displayName':'Time Spent On Challenges',
            'description':'Total time spent in the Challenges section for a particular course.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
        },
        timeSpentOnQuestions:{
            'index': timeSpentOnQuestions,
            'name':'timeSpentOnQuestions',
            'displayName':'Time Spent On Questions',
            'description':'Total time spent in the Questions section for a particular course.',
            'eventsWhichCanChangeThis':[Event.endQuestion], #I'm not sure this makes sense - Keith
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
        },
        consecutiveDaysLoggedIn:{
            'index':consecutiveDaysLoggedIn,
            'name':'consecutiveDaysLoggedIn',
            'displayName':'Consecutive Days Logged In',
            'description':'The number of consecutive days a student logs in to the One Up website.',
            'eventsWhichCanChangeThis':[Event.userLogin],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
        },
        activitiesCompleted:{
            'index':activitiesCompleted,
            'name':'activitiesCompleted',
            'displayName':'Activities Completed',
            'description':'The number of activities a student has completed for a particular course.',
            'eventsWhichCanChangeThis':[Event.participationNoted],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
        },
        numDaysSubmissionEarlier:{
            'index': numDaysSubmissionEarlier,
            'name':'numDaysSubmissionEarlier',
            'displayName':'Number of Days Submission Earlier',
            'description':'The number of days a submission is turned in earlier than the stated deadline',
            'eventsWhichCanChangeThis':[Event.endChallenge, Event.instructorAction, Event.studentUpload],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.challenge],
        },
        numDaysSubmissionLate:{
            'index': numDaysSubmissionLate,
            'name':'numDaysSubmissionLate',
            'displayName':'Number of Days Submission Late',
            'description':'The number of days a submission is turned in later than the stated deadline',
            'eventsWhichCanChangeThis':[Event.endChallenge, Event.instructorAction, Event.studentUpload],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.challenge],
        },                       
        consecutiveDaysWarmUpChallengesTaken:{
            'index': consecutiveDaysWarmUpChallengesTaken,
            'name':'consecutiveDaysWarmUpChallengesTaken',
            'displayName':'Consecutive Days Warm Up Challenges Taken',
            'description':'The number of consecutive days a student has taken Warm-up challenges.',
            'eventsWhichCanChangeThis':[Event.endChallenge],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
        },
        consecutiveWeeksOnLeaderboard:{
            'index': consecutiveWeeksOnLeaderboard,
            'name':'consecutiveWeeksOnLeaderboard',
            'displayName':'Consecutive Weeks on the Leaderboard',
            'description':'The number of consecutive weeks a student has been at the top 3 positions of the Leaderboard.',
            'eventsWhichCanChangeThis':[Event.leaderboardUpdate],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
        },
        consecutiveClassesAttended:{
            'index': consecutiveClassesAttended,
            'name':'consecutiveClassesAttended',
            'displayName':'Consecutive Classes Attended',
            'description':'The number of consecutive classes a student has attended.',
            'eventsWhichCanChangeThis':[Event.instructorAction],
            'type':'int',
            'objectsDefinedFor':[ObjectTypes.none],
            'functions':{
                'global':getConsecutiveClassesAttended
            },
        },                                              
            
    }
    
objectTypeToObjectClass = {
    ObjectTypes.activity: Activities,
    ObjectTypes.challenge: Challenges,
    ObjectTypes.question: Questions,
}
    
# This is where we evaluate the system variables in their appropriate
# context.
def calculate_system_variable(varIndex,course,student,objectType,objectID):
    print("VarIndex: " + str(varIndex))
    
    systemVar = SystemVariable.systemVariables[varIndex]
    functions = systemVar["functionsForCalculating"]
    if ObjectTypes.none in functions:
        return functions[ObjectTypes.none](course,student)
    else:
        if objectType not in functions:
            return "Error: no function defined to calculate this system variable for the specified object type (or no function defined to calculate it at all)!"
        object = objectTypeToObjectClass.objects.get(pk=objectID)
        return functions[objectType](course,student,object)

def numAttempts(course,student,challenge):
    #Return the number of attempts (looking at only the startChallenge event trigger 801)
    numberOfAttempts = StudentEventLog.objects.filter(course = course, student = student, objectType = ObjectTypes.challenge, objectID = challenge.challengeID, event = Event.endChallenge).count()
    return numberOfAttempts

# Utility function used by other functions.  
def getAllTestScores(course,student,challenge):
    return StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge)

def challengeScore(course,student,challenge):    
    #Return the test score from the fired event
    #Event enum is unspecified because it could be triggered on multiple occasions
    scores = getAllTestScores(course,student,challenge)
    if len(scores) == 0:
        return 0 
    return scores.latest('testScore').testScore #Ensure that only the most recent test score is returned

def activityScore(course,student,activity):
    scores = StudentActivities.objects.filter(activityID = activity, courseID = course, studentID = student)
    if len(scores) == 0:
        return 0
    return scores.latest('timestamp').activityScore

def percentageCorrect(course,student,challenge):
    #Return the actual correct percentage from the fired event
    #Get the student score
    allScores = getAllTestScores(course,student,challenge)
    if allScores.exists():
        testScore = allScores.latest('testScore')
    else:
        return 0

    #Check if denominator is zero to avoid getting a DivideByZero error
    if float(testScore.testTotal) != 0:
        percentCorrect = (float(testScore.testScore)/float(testScore.testTotal)) * 100
    return percentCorrect

def maxTestScore(course,student,challenge)    
    #return the highest test score achieved out of the entire class for a challenge
    if (varIndex == SystemVariable.maxTestScore):
        allTestScores = getAllTestScores(course,student,challenge)
        if len(allTestScores) == 0:
            return 0          
        highestTestScore = allTestScores.latest('testScore') #.latest() also gets the max for an integer value
        return highestTestScore
    
    #return the min test score achieved out of the entire class for a challenge
    if (varIndex == SystemVariable.minTestScore):
        allTestScores = getAllTestScores()
        if len(allTestScores) == 0:
            return 0    
        lowestTestScore = allTestScores.earliest('testScore') #.earliest() also gets the min for an integer value
        return lowestTestScore
    
    
    #return the oldest date from the event log with matching object ID (looking at only the endChallenge event trigger 802)
    if (varIndex == SystemVariable.dateOfFirstAttempt):
        attemptObjectsByDate = StudentEventLog.objects.filter(course = course, student = student,objectType = objectType,objectID = objectID, event = Event.endChallenge).order_by('-timestamp')
        if len(attemptObjectsByDate) > 0:
            return attemptObjectsByDate[0].timestamp
        else:
            return datetime(2000,1,1,0,0,0)

    #return the sum of delta times between StartChallenge and End Challenge events   
    if (varIndex == SystemVariable.timeSpentOnChallenges):
        challengeTimes = StudentChallenges.objects.filter(courseID = course,studentID = student).exclude(endTimestamp__isnull=True) #ensure that the challenge has an endTimestamp
        #Accumulate the elapsed time for all challenges in the database with matching student and course ID's
        #initialize totalTime as arbitrary datetime object in order to accumulate elapsed time
        totalTime = datetime(2000,1,1,0,0,0) #python throws Value Error if the date is too small, otherwise it would have been initialized to all 0's
        for challenge in challengeTimes:
            totalTime+=challenge.endTimestamp - challenge.startTimestamp
        totalTime -= datetime(2000,1,1,0,0,0) #subtract arbitrary value back out, in order to get the accurate elapsed time
        minutes = totalTime.total_seconds()/60 #convert total elapsed time to minutes
        return minutes
             
    #return the sum of delta times between Start Question and End Question events
    if (varIndex == SystemVariable.timeSpentOnQuestions):
        
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


    #Counter that sums every login event for a particular course with a new Day timestamp
    #return the counter
    if (varIndex == SystemVariable.consecutiveDaysLoggedIn):
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
        
        
    #Return the number of Participation Noted events
    if (varIndex == SystemVariable.activitiesCompleted):
        numActivitiesCompleted = StudentEventLog.objects.filter(course = course,student = student,objectType = objectType, event = Event.participationNoted).count()
        return numActivitiesCompleted

    # Return the ID of the current challenge which is active when the rule is being evaluated.
    # In the future we may need to hand matching to challenges or activities or so forth in a more complex manner.
    if (varIndex == SystemVariable.challengeId):
        if (objectType == ObjectTypes.challenge):
            return objectID
        else:
            return -1

    def getDaysBetweenCurrentTimeAndDeadline(challengeID):
        challenge = Challenges.objects.get(pk=challengeID)
        deadline = challenge.endTimestamp
        now = timezone.now()
        diff = deadline-now
        return diff.days

    if (varIndex == SystemVariable.numDaysSubmissionEarlier):
        if (objectType != ObjectTypes.challenge):
            return -1
        else:
            return getDaysBetweenCurrentTimeAndDeadline(objectID)
            
    if (varIndex == SystemVariable.numDaysSubmissionLate):
        if (objectType != ObjectTypes.challenge):
            return -1
        else:
            return -1 * getDaysBetweenCurrentTimeAndDeadline(objectID)

def getConsecutiveClassesAttended():
    # This one we can't actually implement yet because we don't have the data.    
    if (varIndex == SystemVariable.consecutiveClassesAttended):
        return 0
    
    # This one I'm not clear on the meaning of.  Which leaderboard?  Do you have to be there at least one day a week or all week?
    # Are we keeping historical leaderboard data?
    if (varIndex == SystemVariable.consecutiveWeeksOnLeaderboard):
        return 0
    
    #TODO: Actually implement this.
    if (varIndex == SystemVariable.consecutiveDaysWarmUpChallengesTaken):
        return 0