from Badges.enums import Event, ObjectTypes

from datetime import datetime
from Instructors.models import Challenges, Activities, Questions, Topics,\
    ActivitiesCategory
from Instructors.constants import default_time_str, unlimited_constant
from django.utils import timezone
import logging
from billiard.connection import CHALLENGE
from django.conf.urls.static import static
from dateutil.utils import today
from Instructors.views.utils import utcDate

logger = logging.getLogger(__name__)
objectTypeToObjectClass = {
    ObjectTypes.activity: Activities,
    ObjectTypes.challenge: Challenges,
    ObjectTypes.question: Questions,
    ObjectTypes.topic: Topics,
    ObjectTypes.activityCategory: ActivitiesCategory,
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


''' Utility Functions '''

def getTestScores(course,student,challenge):
    ''' Utility function used by other functions. 
        This will return the student submissions for a challenge.
    '''
    from Students.models import StudentChallenges
    return StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=challenge)

def getActivityScores(course, student, activity):
    ''' Utility function used by other functions. 
        This will return the student submissions for a activity.
    '''
    from Students.models import StudentActivities
    return StudentActivities.objects.filter(activityID = activity, courseID = course, studentID = student)

def getAllTestScores(course,challenge):
    ''' Utility function used by other functions. 
        This will return the all students submissions for a challenge.
    '''
    from Students.models import StudentChallenges
    return StudentChallenges.objects.filter(courseID=course, challengeID=challenge).exclude(studentID__isTestStudent=True)

def getAllActivityScores(course, activity):
    ''' Utility function used by other functions.
        This will return the all students submissions for a activity.
    '''
    from Students.models import StudentActivities
    return StudentActivities.objects.filter(courseID=course, activityID=activity).exclude(studentID__isTestStudent=True)

def getScorePercentage(course,student, challenge):
    ''' Utility function used by other functions.
        Returns the score percentage of the latest student submission of a challenge'''
    from Students.models import StudentChallenges
    studentChallenges = StudentChallenges.objects.filter(courseID=course,studentID=student, challengeID=challenge)
    entirePoints = 0.0
    earnedPoints = 0.0
    for studentChallenge in studentChallenges:
        entirePoints = studentChallenge.challengeID.getCombinedScore()
        earnedPoints = studentChallenge.getScore()
                
    if entirePoints != 0.0:
        return ((float(earnedPoints) / float(entirePoints)) * 100)
    else:
        return 0

def getAveragePercentageScore(course, student, challenge):
    ''' Utility function used by other functions.
        Returns the percentage of the average score
        a student has scored in a challenge
        ex. scores=[10, 5, 2], numberOfScores = 3, testTotal = 10, percentage = 56.7%
    '''
    allScores = getTestScores(course, student, challenge)
    percentage = 0
    if allScores.exists():
        testTotal = allScores[0].challengeID.getCombinedScore()
        if testTotal == 0:
            return percentage
        scoreList = [c.getScore() for c in allScores]
        numberOfScores = len(scoreList)
        percentage = round(((sum(scoreList)/numberOfScores)/testTotal) * 100, 1)
        logger.debug("Challenge Average Percentage: " + str(percentage) + "%")
        return percentage
    return percentage

def getUniqueChallengesGreaterThanPercentage(course, student, isGraded, percentage):
    ''' Utility function used by other functions.
        Returns the number of challenges greater than some percentage.
        isGraded when True is serious
        isGraded when False is warmup
    '''
    challengesGreaterThan = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=isGraded)
    for challenge in challenges:
        # Get the highest percentage correct from challenge. Also checks to see if student has taken that challenge
        percent_of_max_score = getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge)
        if percent_of_max_score > percentage:
            challengesGreaterThan += 1
    return challengesGreaterThan
    
def getDaysDifferenceActity(activity, studentActivity):
    ''' Utility function used by other functions.
        This will return the number of days between the student submission and activity deadline.
    '''
    from Students.models import StudentFile

    deadline = activity.deadLine
    submission = StudentFile.objects.all.filter(activity = studentActivity).latest("timestamp").timestamp
    # print("getDaysDifferenceActity")
    # print("Deadline ", deadline)
    # print("submission", submission)
    numDays = str(deadline - submission)
    # print(numDays)
    if numDays[0]== "-":
        i=0
        for x in numDays:
            if x==" ":
                return -1 * int(numDays[1:i])
            i+=1
    i=0
    for x in numDays:
        if x==" ":
            return int(numDays[0:i])
        i+=1

def getDaysBetweenCurrentTimeAndDeadline(challenge):
    ''' Utility function used by other functions.
        Returns the number of days between now and challenge deadline.
    '''
    deadline = challenge.dueDate
    now = utcDate()
    diff = deadline-now
    return diff.days

def getTimeSpentOnChallenges(course, student, isGraded):
    ''' Utility function used by other functions.
        Returns the total time in minutes a student has spent on challenges.
        isGraded when True is serious
        isGraded when False is warmup
    '''
    from Students.models import StudentChallenges
    # This calculates the time for both serious and warmup challenges
    #return the sum of delta times between StartChallenge and End Challenge events   
    challengeTimes = StudentChallenges.objects.filter(courseID = course,studentID = student, challengeID__isGraded=isGraded).exclude(endTimestamp__isnull=True) #ensure that the challenge has an endTimestamp
    #Accumulate the elapsed time for all challenges in the database with matching student and course ID's
    #initialize totalTime as arbitrary datetime object in order to accumulate elapsed time
    totalTime = datetime(2000,1,1,0,0,0) #python throws Value Error if the date is too small, otherwise it would have been initialized to all 0's
    for challenge in challengeTimes:
        totalTime+=challenge.endTimestamp - challenge.startTimestamp
    totalTime -= datetime(2000,1,1,0,0,0) #subtract arbitrary value back out, in order to get the accurate elapsed time
    minutes = totalTime.total_seconds()/60 #convert total elapsed time to minutes
    return minutes

def getAllChallenges(course,student, isGraded):
    ''' Utility function used by other functions.
        Returns the total score for either a serious or warmup challenge.
        isGraded when True is serious
        isGraded when False is warmup
    '''
    from Students.models import StudentChallenges
    from Instructors.models import ChallengesQuestions
    challengeQuestions = []
    #get all the challenges for the course, and depending on isGraded(serious=true,warmup=false)
    challenges = StudentChallenges.objects.filter(courseID=course, studentID=student)
    
    for challenge in challenges:
        challengeQuestions.append(list(ChallengesQuestions.objects.filter(challengeID=challenge.challengeID)))
      
    staticList = []
    dynamicList = [] 
    for challengeItem in challengeQuestions:
        for item in challengeItem:
            if item.challengeID.isGraded == isGraded:
                if item.questionID.type == 6 or item.questionID.type == 7:
                    if item.questionID not in dynamicList:
                        dynamicList.append(item.questionID)
                else:
                    if item.questionID not in staticList:
                        staticList.append(item.questionID)
              
    totalScore = 0
    for static in staticList:
        totalScore += firstAttemptStatic(static)
        
    for dynamic in dynamicList:
        totalScore += dynamicQuestionMax(dynamic)
            
    return totalScore

def dynamicQuestionMax(questionID):
    ''' Utility function used by other functions.
        Finds the max score for the dynamic problem.
        Dynamic problem types are 6 and 7.
    '''
    from Students.models import StudentChallengeQuestions
    questions = StudentChallengeQuestions.objects.filter(questionID = questionID)
    
    scores = []
    
    #for each question find the max by finding the scores for each question
    for question in questions:
        scores.append(question.questionScore)
    return max(scores)
    
def firstAttemptStatic(questionID):
    ''' Utility function used by other functions.
        Finds the first attempt for the question and returns the score.
    '''
    from Students.models import StudentChallengeQuestions
    question = StudentChallengeQuestions.objects.filter(questionID=questionID).first()
    
    if question == None:
        return 0
    else:
        return question.questionScore


''' System Variables Functions '''

def challengeScore(course,student,challenge):    
    ''' This will return the latest challenge submission test score (score + score adjustment + curve).'''
    #Return the test score from the fired event
    #Event enum is unspecified because it could be triggered on multiple occasions
    scores = getTestScores(course,student,challenge)
    if len(scores) == 0:
        return 0 
    return scores.latest('testScore').getScore() 

def getTotalScoreForWarmupChallenges(course,student):
    ''' This will return the student total score for a warmup challenge'''
    return getAllChallenges(course, student, False)

def getTotalScoreForSeriousChallenges(course,student):
    ''' This will return the student total score for a serious challenge'''
    return getAllChallenges(course, student, True)

def activityScore(course,student,activity):
    ''' This will return the activity score of an activity completed by a student. 
        The score does not include bonus points.
        If activity has not been completed, the score will be 0
    ''' 
    scores = getActivityScores(course,student,activity)
    if len(scores) == 0:
        return 0
    return scores.latest('activityScore').activityScore

def getMaxTestScore(course,student,challenge):   
    ''' This will return the highest score of all the student submissions of a challenge.
        Score is calculated by score + adjustment + curve.'''
    allTestScores = getAllTestScores(course,challenge)
    if len(allTestScores) == 0:
        return 0 
    return allTestScores.latest('testScore').getScore()

def getMinTestScore(course,student,challenge):
    ''' This will return the lowest score of all the student submissions of a challenge.
        Score is calculated by score + adjustment + curve.'''
    allTestScores = getAllTestScores(course,challenge)
    if len(allTestScores) == 0:
        return 0    
    return allTestScores.earliest('testScore').getScore()

def getMaxActivityScore(course, student, activity):
    ''' Return the highest score of an activity for a course'''
    scores = getAllActivityScores(course, activity)
    if len(scores) == 0:
        return 0
    return scores.latest('activityScore').activityScore
        
def getMinActivityScore(course, student, activity):
    ''' Return the lowest score of an activity for a course'''
    scores = getAllActivityScores(course, activity)
    if len(scores) == 0:
        return 0
    return scores.earliest('activityScore').activityScore

def getAverageTestScore(course, student, challenge):    
    ''' Return the average class score for a challenge of a course '''
    
    from Students.models import StudentRegisteredCourses
    
    sum_max_scores = 0.0
    students = StudentRegisteredCourses.objects.filter(courseID=course)
    for _student in students:
        score = getMaxTestScore(course, _student, challenge)
        sum_max_scores += score
    
    return sum_max_scores / len(students)
            
def getAverageActivityScore(course,student, activity):
    ''' Return the average score of an activity for a course'''
    scores = getAllActivityScores(course, activity)
    if len(scores) == 0:
        return 0
    return float(sum([score.activityScore for score in scores])) / float(len(scores))

def getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge):
    ''' This will return the percentage of the highest challenge score obtained by a student
        for a challenge.
        Score does not include bonus points (score + adjustment + curve)
    '''
    allScores = getTestScores(course,student,challenge)
    maxScore = 0
    for score in allScores:
        combinedScore = score.getScore()
        if combinedScore > maxScore:
            maxScore = combinedScore
    
    challengeScore = challenge.getCombinedScore()
    if challengeScore == 0:
        return 0
    return float(maxScore)/float(challengeScore) * 100

def getPercentageOfMaxActivityScore(course, student, activity):
    ''' This will return the percentage of the highest score for a course of a activity'''
    print("percentage of max activity score")
    print(activity)
    highestScore = getMaxActivityScore(course, student, activity)
    
    totalScore = activity.points
    #avoiding division by zer0
    if totalScore != 0:
        print("percentage of score out of max activity score ", (float(highestScore)/float(totalScore))*100.0)
        return ((float(highestScore)/float(totalScore))*100.0)
    else:
        return 0.0

def getPercentageOfCorrectAnswersPerChallengePerStudent(course,student, challenge):
    ''' This will return the student percentage of correctly answered questions out of 
        all the questions for a challenge
    '''
    from Students.models import StudentChallengeQuestions, StudentChallenges
    from Instructors.models import ChallengesQuestions
    questionIds = []
    challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)
    for challenge_question in challenge_questions:
        questionIds.append(challenge_question.questionID)
    
    try:    
        studentChallenge = StudentChallenges.objects.filter(studentID=student, challengeID=challenge, courseID=course).latest('testScore')
    except:
        return 0.00
    
    totalQuestions = len(questionIds)
    correctlyAnsweredQuestions = 0
    for question in questionIds:
        studentQuestion = StudentChallengeQuestions.objects.filter(studentChallengeID=studentChallenge,questionID=question)
        
        if studentQuestion:
            if studentQuestion[0].questionTotal == studentQuestion[0].questionScore:
                correctlyAnsweredQuestions +=1
    
    if correctlyAnsweredQuestions != 0 and totalQuestions != 0:
        return round((float(correctlyAnsweredQuestions)/float(totalQuestions))*100)
    else:
        return 0

def getPercentageOfActivityScore(course, student , activity):
    ''' This will return the percentage of the student's activity 
        score out of the max possible activity score'''

    totalScore = activity.points
    if totalScore != 0:
        return ((float(activityScore(course, student, activity))/float(totalScore)) * 100)
    else:
        return 0

def getScorePercentageDifferenceFromPreviousActivity(course, student, activity):
    ''' This will return the the difference between the percentages of the student's scores for this 
        activity and its previous one.
    '''
    
    from Students.models import StudentActivities 
    
    print(student)
    print(activity.activityName)
     
    # get all activities for this student from the database; order by timestamp
    stud_activities = StudentActivities.objects.all().filter(courseID=course, studentID=student).order_by('timestamp')
    print (stud_activities)
    assignments = []
    for sa in stud_activities:
        assignments.append(sa.activityID)
    #print('assignments',assignments)

    # now work only with the assignments
    # if no activities or just one activity return zero
    if len(assignments)==1 or len(assignments)==0:
        return 0
     
    previousActivityScorePercentage = unlimited_constant #Should never be used if code is correct
    numActivitiesVisited = 0
    
    for assign in assignments:
        numActivitiesVisited += 1
        if assign == activity:
            if numActivitiesVisited == 1:
                #This is the very first activity, we cannot compare it to previous
                
                return 0
            else:
                return getPercentageOfActivityScore(course,student,assign)-previousActivityScorePercentage
        else:
            previousActivityScorePercentage = getPercentageOfActivityScore(course, student, assign)
            
    return 0

def getScoreDifferenceFromPreviousActivity(course, student, activity):
    ''' This will return the student difference of score between this 
        activity and the previous one.'''
        
    from Students.models import StudentActivities 
    #filter database by timestamp
    stud_activities = StudentActivities.objects.all().filter(courseID=course, studentID=student).order_by('timestamp')

    stud_assignments = []
    for sa in stud_activities:
        stud_assignments.append(sa)
            
    print('Stud_asssignments',stud_assignments)

    # now work only with the assignments    
    # if no activities or just one activity return zero
    if len(stud_assignments)==1 or len(stud_assignments)==0:
        return 0
    
    previousActivityScore = unlimited_constant  #Should never be used if code is correct
    numActivitiesVisited = 0
    
    for sa in stud_assignments:
        numActivitiesVisited += 1
        if sa.activityID == activity:            
            if numActivitiesVisited == 1:
                #This is the very first activity, we cannot compare it to previous
                return 0
            else:
                return sa.activityScore-previousActivityScore
        else:
            previousActivityScore = sa.activityScore
            
    return 0

def activityScoreDifferenceFromPreviousAveragedScoresByCategory(course, student, activity):
    ''' This system variable calculates the score difference from the activity provided and 
        the previous activies based on the average of the previous activities percentages and the activity
        category for the student. The previous activities are selected if the activity deadline 
        is less than or equal to the activity provied deadline as well as the activity provided category.

        Author: Austin
        Last Modified by: Austin
    '''
    from Instructors.models import Activities
    from Students.models import StudentActivities 
    print("activity {}".format(activity))
    # Get all the activities within the category that has a deadline earlier than the passed in activity
    activitiesWithCategory = Activities.objects.filter(category = activity.category).filter(deadLine__lte=activity.deadLine)
    # Get the student activities that has a score and is apart of activites with category and order by deadline with the latest being first
    studentActivites = StudentActivities.objects.filter(courseID = course, activityID__in = activitiesWithCategory, studentID = student, graded = True).order_by('-activityID__deadLine')
    if studentActivites.exists():
        latestAttempt = studentActivites.first()
        # Calculate the total of the earlier activities by percentage
        total = sum(int(getPercentageOfActivityScore(course, student, act)) for act in studentActivites[1:])
        count = studentActivites.count()-1
        if count <= 0:
            print("Total: " + str(total))
            print("latest Score: " + str(latestAttempt.activityScore))
            return 0
        # Calculate the average
        average = total/count
        print("Total: " + str(total))
        print("Average: "+ str(average))
        print("latest Score: " + str(latestAttempt.activityScore))
        # The students' last attempt has earned more than their average return the difference
        if latestAttempt.activityScore > average:
            return float(latestAttempt.activityScore) - average
    return 0
    
def getAverageTestScorePercent(course, student, challenge):    
    '''return the course average score of the a challenge, adjustment and curve are considered'''
   
    from Students.models import StudentRegisteredCourses
    from Students.models import StudentChallenges
    
    students = StudentRegisteredCourses.objects.filter(courseID=course)
    max_scores = 0 
    chall = 0
    for student in students:
        try: 
            max_score = StudentChallenges.objects.filter(courseID=course, studentID=student.studentID, challengeID=challenge).latest('testScore').getScore()
            max_scores += max_score
            chall += 1
            print('here student', student)
        except:
            print('here')
            continue
    if not chall == 0 and not challenge.totalScore == 0: 
        ave = (max_scores / (chall * challenge.totalScore)) * 100
        print("Get average test score percentage", ave)
        return ave
    else:
        print("Get average test score percentage", 0)
        return 0
   

    
def getDateOfFirstChallengeSubmission(course,student,challenge):
    ''' This will return the date (not datetime) of the first submission of a challenge for a student.
        If no submission is found, the date of 1/1/200 will be returned
    '''
    from Students.models import StudentEventLog
    #return the oldest date from the event log with matching object ID (looking at only the endChallenge event trigger 802)
    attemptObjectsByDate = StudentEventLog.objects.filter(course = course, student = student,objectID = challenge.challengeID,objectType = ObjectTypes.challenge, event = Event.endChallenge).order_by('-timestamp')
    if len(attemptObjectsByDate) > 0:
        return attemptObjectsByDate[0].timestamp.date()
    else:
        return datetime(2000,1,1,0,0,0).date()

def earliest_challenge_submission_in_class(course, student, challenge):
    ''' This will return the date of the earliest submission of a particular challenge in a course.'''
    from Students.models import StudentChallenges

    earliest_submission = datetime(2000,1,1,0,0,0).date()
    student_submissions = list(StudentChallenges.objects.filter(courseID=course, challengeID=challenge).exclude(endTimestamp__isnull=True).values_list('endTimestamp', flat=True))
    if len(student_submissions) <= 0:
        return earliest_submission
    earliest_submission = min(student_submissions)
    print("[DATE] {}".format(earliest_submission.date()))
    return earliest_submission.date()

def sc_reached_due_date(course, student, serious_challenge):
    ''' This will return True/False if the serious challenge due date has been reached
        or the due date has a default date (not set)
    '''
    if not serious_challenge.isGraded:
        return False
    return serious_challenge.dueDate.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") == default_time_str or datetime.now(tz=timezone.utc).replace(microsecond=0) >= serious_challenge.dueDate.replace(microsecond=0)

def isWarmUpChallenge(course,student,challenge):
    ''' This will return True/False if the a particular challenge is a warmup challenge'''
    return not challenge.isGraded

def totalTimeSpentOnChallenges(course,student):
    ''' This will return the total minutes a student has spent completing any challenges'''
    return getTimeSpentOnChallenges(course, student, True) + getTimeSpentOnChallenges(course, student, False)

def getTotalMinutesSpentOnWarmupChallenges(course, student):
    ''' This will return the number of minutes a student has spent on all warmup challenges'''    
    minutes = getTimeSpentOnChallenges(course, student, False)
    logger.debug("Total minutes spent on warmup challenges: " + str(minutes))
    return minutes

def getTotalMinutesSpentOnSeriousChallenges(course, student):
    ''' This will return the number of minutes a student has spent on all serious challenges'''    
    minutes = getTimeSpentOnChallenges(course, student, True)
    logger.debug("Total minutes spent on serious challenges: " + str(minutes))
    return minutes

def totalTimeSpentOnQuestions(course,student):
    ''' INCOMPLETE...
        This will return the total time in minutes a student has spent on questions
    '''
    from Students.models import StudentEventLog
    #return the sum of delta times between Start Question and End Question events
    
    #TODO: Code assumes that question start times and question end times will come back in the same order.
    # This is not a fair assumption and this code should be rewritten to match the starts and ends together.
    # Also if a student starts a challenge and then abandons it, the counts will not be equal and then this code
    # will always return None for that student in that course.
    
    if(type(course) != int):
        course = course.pk
        print(course)

    
    questionStartTimes = StudentEventLog.objects.filter(course = course,student = student, event = Event.startQuestion)
    questionEndTimes = StudentEventLog.objects.filter(course = course,student = student, event = Event.endQuestion)
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

def getConsecutiveScoresDifference(course, student, challenge):
    ''' This will return the score difference between a particular student completed challenge score and
        student previous completed challenge score
    '''
    from Students.models import StudentChallenges, StudentEventLog
    
    difference = 0
    logger.debug(challenge)
    # Get the last challenge the student has taken whether it's a warmpup or serious challenge
    studentLastChallengeEvent = StudentEventLog.objects.filter(course = course, student = student, objectType = ObjectTypes.challenge, event = Event.endChallenge).exclude(objectID = challenge.challengeID).order_by('-timestamp')
    if studentLastChallengeEvent:
        studentLastChallengeEvent = studentLastChallengeEvent[0]
        studentLastChallenge = StudentChallenges.objects.filter(courseID = course, studentID=student, challengeID = studentLastChallengeEvent.objectID)
        if studentLastChallenge.exists():
            # Get both challenges highest test score
            latestScore = challengeScore(course,student, studentLastChallengeEvent.objectID)
            previousScore = challengeScore(course, student, challenge)
            logger.debug(latestScore)
            logger.debug(previousScore)
            
            difference = abs(previousScore - latestScore)
            logger.debug("Difference between last challenge score: " + str(difference))
            return difference
            
    return difference

def getConsecutiveDaysLoggedIn(course,student):
    ''' This will return the number of days a student has logged in.'''
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

def getConsecutiveDaysWarmUpChallengesTaken30Percent(course,student,challenge): 
    ''' This will return the number of consecutive days a student has taken a warmup challenge
        with a score >= 30%
    '''
    from Students.models import StudentEventLog
    warmUpChallDates = []
    # filter all the ended challenge events
    eventObjects = StudentEventLog.objects.filter(student=student, course=course,event = Event.endChallenge)
    for event in eventObjects:
        if event.objectType == ObjectTypes.challenge: 
            # get a specific challenge by its ID
            try:
                chall = Challenges.objects.get(courseID=course, challengeID=event.objectID)
                print("Challenge Name : " + chall.challengeName)
            except:
                continue
              
            scorePecentage = getScorePercentage(course,student,event.objectID)
            # if the challenge is not graded then it's a warm up challenge and put in it in the list
            if not chall.isGraded and scorePecentage >= 30.0:
                # eventDate = str(event.timestamp
                print("Time : ", event.timestamp.date())
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
        for date in warmUpChallDates[1:len(warmUpChallDates)]: 
            if str(date - previousDate) == "1 day, 0:00:00":
                consecutiveDays +=1
                previousDate = date
            elif str(date - previousDate) == "0:00:00":
                continue
            else:
                consecutiveDays = 1
                previousDate = date 
                
        print("consecutive days :", consecutiveDays)  
        # if the last day the challenge taken is not today then return 0
        if warmUpChallDates[len(warmUpChallDates)-1] != today:
            consecutiveDays = 0
        print("consecutive days 1:", consecutiveDays)
        print()
        print()
        return consecutiveDays

def getConsecutiveDaysWarmUpChallengesTaken75Percent(course,student,challenge): 
    ''' This will return the number of consecutive days a student has taken a warmup challenge
        with a score >= 75%
    '''
    from Students.models import StudentEventLog
    warmUpChallDates = []
    # filter all the ended challenge events
    print()
    print(student)
    eventObjects = StudentEventLog.objects.filter(student=student, course=course,event = Event.endChallenge)
    for event in eventObjects:
        if event.objectType == ObjectTypes.challenge: 
            # get a specific challenge by its ID
            
            try:
                chall = Challenges.objects.get(courseID=course, challengeID=event.objectID)
                print("Challenge Name : " + chall.challengeName)
            except:
                continue
            
            scorePecentage = getScorePercentage(course,student, event.objectID)
            # if the challenge is not graded then it's a warm up challenge and put in it in the list
            if not chall.isGraded and scorePecentage >= 75.0:
                # eventDate = str(event.timestamp)
                print("Time : ", event.timestamp.date())
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
        for date in warmUpChallDates[1:len(warmUpChallDates)]: 
            if str(date - previousDate) == "1 day, 0:00:00":
                consecutiveDays +=1
                previousDate = date
            elif str(date - previousDate) == "0:00:00":
                continue
            else:
                consecutiveDays = 1
                previousDate = date 
        print("consecutive days :", consecutiveDays)
        # if the last day the challenge taken is not today then return 0
        if warmUpChallDates[len(warmUpChallDates)-1] != today:
            consecutiveDays = 0
        print("consecutive days 1:", consecutiveDays)
        return consecutiveDays    


def getNumDaysSubmissionLateActivity(course, student , activity):
    '''Return the number of days an activity submitted after due date'''
    from Students.models import StudentActivities
   
    print("numb days submissionsssss late")
    studentActivity = StudentActivities.objects.filter(courseID=course, studentID=student, activityID=activity)
    if not studentActivity:
        return (float('inf'))
    else: 
        print("submission late " , getDaysDifferenceActity(activity,studentActivity[0]))
        return (-1 *getDaysDifferenceActity(activity,studentActivity[0]))
    
def getNumDaysSubmissionEarlyActivity(course, student , activity):
    '''Return the number of days an activity submitted before due date'''
    from Students.models import StudentActivities
    
    studentActivity = StudentActivities.objects.filter(courseID=course, studentID=student, activityID=activity)
    if not studentActivity:
        return (-1*float('inf'))
    else:
        return getDaysDifferenceActity(activity,studentActivity[0])

def calcNumDaysSubmissionEarly(course,student,challenge):
    days = getDaysBetweenCurrentTimeAndDeadline(challenge)
    return days
        
def calcNumDaysSubmissionLate(course,student,challenge):
    days = -1 * getDaysBetweenCurrentTimeAndDeadline(challenge)
    return days


# def getScorePercentageDifferenceFromPreviousActivity(course, student, activity):
#     '''Returns the the difference between the percentages of the student's scores for this activity and its previous one'''
#     
#     from Students.models import StudentActivities 
#     
#     #filter database by timestamp
#     activityObjects = StudentActivities.objects.all().filter(courseID=course, studentID=student).order_by('timestamp')
#     
#     #if the activity is the very first one then return zero
#     if len(activityObjects)==1 or len(activityObjects)==0:
#         return 0
#     
#     previousActivityScorePercentage = unlimited_constant #Should never be used if code is correct
#     numActivitiesVisited = 0
#     for activityObject in activityObjects:
#         numActivitiesVisited += 1
#         if activityObject.activityID == activity:
#             if numActivitiesVisited == 1:
#                 #This is the very first activity, we cannot compare it to previous
#                 return 0
#             else:
#                 return getPercentageOfActivityScore(course,student,activityObject.activityID)-previousActivityScorePercentage
#         else:
#             previousActivityScorePercentage = getPercentageOfActivityScore(course, student, activityObject.activityID)
#             
#     return 0


def getNumAttempts(course,student,challenge):
    ''' This will return the number of times a student has completed a specific challenge. ''' 
    from Students.models import StudentEventLog
    #Return the number of attempts (looking at only the startChallenge event trigger 801)
    numberOfAttempts = StudentEventLog.objects.filter(course = course, student = student, objectType = ObjectTypes.challenge, objectID = challenge.challengeID, event = Event.startChallenge).count()
    return numberOfAttempts

def getActivitiesCompleted(course,student):
    ''' This will return the number of activities a student has participated in.'''
    from Students.models import StudentEventLog
    numActivitiesCompleted = StudentEventLog.objects.filter(course = course,student = student,objectType = ObjectTypes.activity, event = Event.participationNoted).count()
    return numActivitiesCompleted

def getNumberOfBadgesEarned(course, student):
    ''' This will return the number of badges a student has earned'''
    from Students.models import StudentBadges
    count = StudentBadges.objects.filter(studentID = student).count()
    logger.debug("Number of Earned Badges by student: " + str(count))
    return count

def getNumberOfDuelsSent(course, student):
    ''' This will return the number of duels sent by a student regardless of the
        outcome of the duel
    '''
    from Students.models import DuelChallenges
    sent = len(DuelChallenges.objects.filter(challenger=student, courseID=course))
    return sent

def getNumberOfDuelsAccepted(course, student):
    ''' This will return the number of duels a student has accepted sent by any other
        student.
        Status -> indicates the status of the challenge 0=canceled ,1=pending, 2=accepted
    '''
    from Students.models import DuelChallenges
    accepted = len(DuelChallenges.objects.filter(challengee=student, courseID=course, status=2))
    return accepted

def getNumberOfDuelsWon(course, student):
    ''' This will return the number of wins the student has earned for every duel 
        in the course
    '''
    from Students.models import Winners
    wins = len(Winners.objects.filter(studentID=student, courseID=course))
    return wins

def getNumberOfDuelsParticipated(course, student):
    ''' This will return the number of duels the student has participated
        in the course regarless of the outcome of the duel
        Status -> indicates the status of the challenge 0=canceled ,1=pending, 2=accepted
    '''
    from Students.models import DuelChallenges
    from Students.models import StudentChallenges
    from datetime import timedelta

    print("student", student)

    sent = DuelChallenges.objects.filter(challenger=student, courseID=course, status=2)
    requested = DuelChallenges.objects.filter(challengee=student, courseID=course, status=2)
    
    duels = list(sent) + list(requested)
    print("duels", duels)

    count = 0
    for duel in duels:
        print("duel", duel)
        print("challenge", duel.challengeID)
        if StudentChallenges.objects.filter(challengeID=duel.challengeID, courseID=course):
            chall = StudentChallenges.objects.filter(challengeID=duel.challengeID, courseID=course).earliest('endTimestamp')
            if chall.endTimestamp <= (duel.acceptTime +timedelta(minutes=duel.startTime) +timedelta(minutes=duel.timeLimit) +timedelta(seconds=6)):
                print("Participated challenge", duel.challengeID.challengeName)
                count += 1
    return count


def getNumberOfDuelsLost(course, student):
    ''' This will return the number of duel lost the student has for every duel 
        in the course
    '''
    from Students.models import DuelChallenges
    from Students.models import Winners

    duel_challenges = DuelChallenges.objects.filter(challenger=student, courseID=course)
    duel_wins = Winners.objects.filter(studentID=student, courseID=course)
    
    count = 0
    for duel_win in duel_wins:
        if duel_win.DuelChallengeID in duel_challenges:
            count += 1

    return count

def getNumberOfCalloutSent(course, student):
    ''' This will return the number of call outs sent by a student regardless of weather sender won or not
    '''
    from Students.models import Callouts
    sent = len(Callouts.objects.filter(sender=student, courseID=course))
    return sent

def getNumberOfCalloutParticipate(course, student):
    ''' This will return the number of call outs a student has participated in sent by any other
        student regardless of weather participant won or not.
    '''
    from Students.models import CalloutStats
    return len(CalloutStats.objects.filter(studentID=student, courseID=course))

def getNumberOfCalloutRequested(course, student):
    ''' This will return the number of call outs a student has been requested, sent by any other
        student regardless of weather participant won or not.
    '''
    from Students.models import CalloutParticipants
    return len(CalloutParticipants.objects.filter(participantID=student, courseID=course))
    
def getNumberOfCalloutParticipationWon(course, student):
    ''' This will return the number of wins the student has earned for every requested call out 
        in the course 
    '''
    from Students.models import CalloutParticipants
    return len(CalloutParticipants.objects.filter(participantID=student, courseID=course, hasWon=True))

def getNumberOfCalloutParticipationLost(course, student):
    ''' This will return the number of lost the student has for every requested call out 
        in the course 
    '''
    from Students.models import CalloutParticipants
    return len(CalloutParticipants.objects.filter(participantID=student, courseID=course, hasWon=False, hasSubmitted=True))

def getNumberOfUniqueSeriousChallengesAttempted(course, student):
    ''' Get the number of unique serious challenges the student has taken.'''    
    challenges = Challenges.objects.filter(courseID=course, isGraded=True)
    attempted = 0
    for challenge in challenges:
        studentChallenges = getNumAttempts(course, student, challenge)
        if studentChallenges > 0:
            attempted += 1
    
    logger.debug("Serious Challenges Attempted: " + str(attempted))
    return attempted

def getNumberOfUniqueWarmupChallengesAttempted(course, student):
    ''' Get the number of warmup challenges the student has taken.'''    
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    attempted = 0
    for challenge in challenges:
        studentChallenges = getNumAttempts(course, student, challenge)
        if studentChallenges > 0:
            attempted += 1
    
    logger.debug("Warmup Challenges Attempted: " + str(attempted))
    return attempted
            
def getNumberOfUniqueSeriousChallengesGreaterThan30Percent(course, student):  
    ''' This will return the number of unique serious challenges that a student completed with a 
        score > 30%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, True, 30.0)
    logger.debug("Number of unqiue serious challenges > 30%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueSeriousChallengesGreaterThan75Percent(course, student):  
    ''' This will return the number of unique serious challenges that a student completed with a 
        score > 75%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, True, 75.0)
    logger.debug("Number of unqiue serious challenges > 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueSeriousChallengesGreaterThan90Percent(course, student):  
    ''' This will return the number of unique serious challenges that a student completed with a 
        score > 90%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, True, 90.0)
    logger.debug("Number of unqiue serious challenges > 90%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan30Percent(course, student):  
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score > 30%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 30.0)
    logger.debug("Number of unqiue warmup challenges > 30%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan75Percent(course, student): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score > 75%
    '''   
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 75.0)
    logger.debug("Number of unqiue warmup challenges > 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan90Percent(course, student):  
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score > 90%
    '''
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 90.0)
    logger.debug("Number of unqiue warmup challenges > 90%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic(course, student, topic): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score > 75% for a particular topic
    '''
    from Instructors.models import ChallengesTopics   
    challengesGreaterThan = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in challenges:
        # If topic is assigned to the warmup challenge then find percentage
        challengeTopics = ChallengesTopics.objects.filter(topicID=topic, challengeID = challenge.challengeID)
        if challengeTopics.exists():
            percentage = getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge)
            if percentage > 75.0:
                challengesGreaterThan += 1
    logger.debug("Number of unqiue warmup challenges with specific topic > 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt(course, student): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score > 75% that the student has only completed once
    '''   
    numberOfChall = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in challenges:
        allScores = getTestScores(course,student,challenge)
        if len(allScores)==1:
            percentage = getScorePercentage(course, student, challenge)
            if percentage > 75:
                numberOfChall += 1
    print("Number of unqiue warmup challenges > 75%: " ,numberOfChall)
    return numberOfChall

class SystemVariable():
    numAttempts = 901 # The total number of attempts that a student has given to a challenge
    score = 902 # The score for the challenge or activity
    maxTestScore = 904 # The maximum of the test scores of all the student's attempts for a particular challenge
    minTestScore = 905 # The minimum of the test scores of all the student's attempts for a particular challenge
    dateOfFirstChallengeSubmission = 906 # The date on which the student has submitted a particular challenge for the first time.
    timeSpentOnChallenges = 907 # Time spent on a particular challenge.
    timeSpentOnQuestions = 908 # Time spent on a particular question. INCOMPLETE
    consecutiveDaysLoggedIn = 909 # The number of consecutive days a student logs in to the One Up website
    activitiesCompleted = 910 # The number of activities a student has completed for a particular course
    numDaysSubmissionEarlier = 912 #Number of days an assignment is submitted earlier INCOMPLETE
    numDaysSubmissionLate = 913 #Number of days an assignment is submitted late INCOMPLETE
    averageTestScore = 914  # Average Test Score INCOMPLETE
    consecutiveDaysWarmUpChallengesTaken30Percent = 917 #Consecutive days warm up challenges at least 30% correct are taken
    consecutiveDaysWarmUpChallengesTaken75Percent = 918 #Consecutive days warm up challenges at least 75% correct are taken
    percentOfScoreOutOfMaxChallengeScore = 919  # percentage of student's score (for the max scored attempt ) out of the max possible challenge score
    uniqueSeriousChallengesAttempted = 920 # The number of unique serious challenges completed by the student
    uniqueWarmupChallengesGreaterThan30Percent = 921 # Number of warmup challenges with a score percentage greater than 30%
    uniqueWarmupChallengesGreaterThan75Percent = 922 # Number of warmup challenges with a score percentage greater than 75%
    uniqueWarmupChallengesGreaterThan75PercentForTopic = 923 # Number of warmup challenges with a score percentage greater than 75% for a particular topic
    totalMinutesSpentOnWarmupChallenges = 924 # Total minutes spent on warmup challenges only
    differenceFromLastChallengeScore = 925 # Score difference from last complete challenge/warmup challenge and a specific challenge
    averageActivityScore = 928 # average activity score of the course 
    percentageOfCorrectAnswersPerChallengePerStudent = 931 #percentage of correctly answered questions out of all the questions
    isWarmUp = 932 # is a warm-up challenge
    activityScoreDifferenceByCategory = 941
    scorePercentageDifferenceFromPreviousActivity = 934 # Difference between the percentages of the student's scores for this activity and the one preceding it'''      
    percentageOfActivityScore = 935 # Percentage of the student's score out of the max possible score for this activity
    percentageOfMaxActivityScore = 936 # Percentage of the highest score for the course out of the max possible score for this activity
    uniqueWarmupChallengesAttempted = 937 # The number of unique challenges completed by the student
    badgesEarned = 938 # Number of badges student as earned
    scoreDifferenceFromPreviousActivity = 939 # score difference from previous activity
    uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt = 940 #The number of warmup challenges with a score greater than 75% with only one attempt.
    totalScoreForSeriousChallenges = 942
    totalScoreForWarmupChallenges = 943    
    seriousChallengeReachedDueDate = 944 
    uniqueWarmupChallengesGreaterThan90Percent = 945 
    uniqueSeriousChallengesGreaterThan90Percent = 946 # Number of serious challenges with a score percentage greater than 90%
    earliestChallengeSubmissionInClass = 947 # Returns the date of the earliest challenge submission
    uniqueSeriousChallengesGreaterThan30Percent = 948
    uniqueSeriousChallengesGreaterThan75Percent = 949
    totalMinutesSpentOnSeriousChallenges = 950
    duelsSent = 951 # Returns the number of duels a student has sent (completed duels only)
    duelsAccepted = 952 # Returns the number of duels a student has accepted (completed duels only)
    duelsWon = 953 # Returns the number of duels a student has won
    duelsLost = 954 # Returns the number of duels a student has lost
    calloutSent = 955 # Returns the number of callout a student has sent
    calloutParticipate = 956 # Returns the number of callout a student has participated in 
    calloutParticipationWon = 957 # Returns the number of callout a student has participated in and won
    calloutParticipationLost = 958 # Returns the number of callout a student has participated in and lost
    calloutRequested = 959 #
    duelsParticipated = 960 # Return the number of duels a student has participated in regarless of the duel outcome


    systemVariables = {
        score:{
            'index': score,
            'name':'score',
            'displayName':'Score',
            'description':'The completed activity or challenge score by a student. The student activity score does not include bonus points. The student challenge score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge, Event.adjustment],
                ObjectTypes.activity:[Event.participationNoted,],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: activityScore,
                ObjectTypes.challenge: challengeScore
            }    
        },
        totalScoreForWarmupChallenges:{
            'index': totalScoreForWarmupChallenges,
            'name':'totalScoreForWarmupChallenges',
            'displayName':'Warmup Challenge Total Score',
            'description':'The student total score for a warmup challenge. Takes the earned points only from the first attempt of each challenge for the static problems but the highest score for the dynamic problems',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalScoreForWarmupChallenges
            },
        },
        totalScoreForSeriousChallenges:{
            'index': totalScoreForSeriousChallenges,
            'name':'totalScoreForSeriousChallenges',
            'displayName':'Serious Challenge Total Score',
            'description':'The student total score for a serious challenge. Takes the earned points only from the first attempt of each challenge for the static problems but the highest score for the dynamic problems',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalScoreForSeriousChallenges
            },
        },
        maxTestScore:{
            'index': maxTestScore,
            'name':'maxTestScore',
            'displayName':'Highest Score',
            'description':"The highest score of all student submissions for a particular challenge or activity. The student activity score does not include bonus points. The student challenge score only includes the student score, adjustment, and curve.",
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[ Event.challengeExpiration, Event.adjustment],
                ObjectTypes.activity: [Event.participationNoted]
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getMaxTestScore,
                ObjectTypes.activity: getMaxActivityScore
            }
        },
        minTestScore:{
            'index': minTestScore,
            'name':'minTestScore',
            'displayName':'Lowest Score',
            'description':"The lowest score of all student submissions for a particular challenge or activity. The student activity score does not include bonus points. The student challenge score only includes the student score, adjustment, and curve.",
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[ Event.challengeExpiration,Event.adjustment],
                ObjectTypes.activity: [Event.participationNoted]
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getMinTestScore,
                ObjectTypes.activity: getMinActivityScore
            }
        },
        averageTestScore:{
            'index': averageTestScore,
            'name':'averageTestScore',
            'displayName':'Average Test Score',
            'description':'The students average for a challenge. Using the best score from each student',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge,Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getAverageTestScore
            },
        }, 
        averageActivityScore:{
            'index':averageActivityScore,
            'name':'averageActivityScore',
            'displayName':'Average Activity Score',
            'description':'The average activity score of all students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: getAverageActivityScore
            }
        },
        percentOfScoreOutOfMaxChallengeScore:{
            'index': percentOfScoreOutOfMaxChallengeScore,
            'name':'percentOfScoreOutOfMaxChallengeScore',
            'displayName':'Percentage of Student Max Score Out of Challenge Score',
            'description':'The percentage of the student max score for a particular challenge. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getPercentOfScoreOutOfMaxChallengeScore
            },
        },  
        percentageOfMaxActivityScore:{
            'index': percentageOfMaxActivityScore,
            'name':'percentageOfMaxActivityScore',
            'displayName':'Percentage of a Activity Max Score for the Course',
            'description':'Percentage of the highest score for the course out of the max possible score for this activity',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity:[Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity:getPercentageOfMaxActivityScore
            },
        },
        percentageOfCorrectAnswersPerChallengePerStudent:{
            'index': percentageOfCorrectAnswersPerChallengePerStudent,
            'name':'percentageOfCorrectAnswersPerChallengePerStudent',
            'displayName':'Percentage of Correctly Answered Questions',
            'description':'The student percentage of correctly answered questions out total number of questions for a challenge',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getPercentageOfCorrectAnswersPerChallengePerStudent
            },
        }, 
        percentageOfActivityScore:{
            'index': percentageOfActivityScore,
            'name':'percentageOfActivityScore',
            'displayName':'Percentage of Student Score for this Activity',
            'description':'Percentage of the student score out of the max possible score for this activity',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity:[Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity:getPercentageOfActivityScore
            },
        }, 
        scorePercentageDifferenceFromPreviousActivity:{
            'index': scorePercentageDifferenceFromPreviousActivity,
            'name':'scorePercentageDifferenceFromPreviousActivity',
            'displayName':'Score Percentage Difference of Activity and Its Preceding Activity',
            'description':'The student difference of the score percentage of this activity from the activity preceding it',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity:[Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity:getScorePercentageDifferenceFromPreviousActivity
            },
        },
        scoreDifferenceFromPreviousActivity:{
            'index': scoreDifferenceFromPreviousActivity,
            'name':'scoreDifferenceFromPreviousActivity',
            'displayName':'Score Difference from Previous Completed Activity',
            'description':'The student score difference of an activity from the activity preceding it',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity:[Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity:getScoreDifferenceFromPreviousActivity
            },
        },
        activityScoreDifferenceByCategory:{
            'index': activityScoreDifferenceByCategory,
            'name':'activityScoreDifferenceFromPreviousAveragedScoresByCategory',
            'displayName':'Score Difference From Averaged Previous Activities Scores For Activity Category',
            'description':'The student score difference from averaged previous activities scores based on a particular activity category',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: activityScoreDifferenceFromPreviousAveragedScoresByCategory
            },
        },
        dateOfFirstChallengeSubmission:{
            'index': dateOfFirstChallengeSubmission,
            'name':'dateOfFirstChallengeSubmission',
            'displayName':'Date of First Challenge Submission',
            'description':'The date on which the student has completed a particular challenge for the first time',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.startChallenge],
            },
            'type':'date',
            'functions':{
                ObjectTypes.challenge: getDateOfFirstChallengeSubmission
            }
        },
        earliestChallengeSubmissionInClass:{
            'index': earliestChallengeSubmissionInClass,
            'name':'earliestChallengeSubmissionInClass',
            'displayName':'Earliest Challenge Submission in Course',
            'description':'The date of the earliest submission of a particular challenge by any student in the course',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge],
            },
            'type':'date',
            'functions':{
                ObjectTypes.challenge:earliest_challenge_submission_in_class
            },
        },
        seriousChallengeReachedDueDate:{
            'index': seriousChallengeReachedDueDate,
            'name': 'seriousChallengeReachedDueDate',
            'displayName': 'Serious Challenge Has Reached Due Date',
            'description': 'True if the serious challenge due date has been reached, otherwise false',
            'eventsWhichCanChangeThis': {
                ObjectTypes.challenge: [Event.challengeExpiration],
            },
            'type': 'boolean',
            'functions': {
                ObjectTypes.challenge: sc_reached_due_date
            },
        },
        isWarmUp:{
            'index': isWarmUp,
            'name': 'isWarmUp',
            'displayName': 'Is WarmUp Challenge',
            'description': 'True if the challenge in question is a warmup challenge else it is false since the challenge is of Serious Type',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge],
            },
            'type':'boolean',
            'functions':{
                ObjectTypes.challenge:isWarmUpChallenge
            },
        },
        timeSpentOnChallenges:{
            'index': timeSpentOnChallenges,
            'name':'timeSpentOnChallenges',
            'displayName':'Time Spent On Challenges (Minutes)',
            'description':'The total time in minutes a student has spent completing challenges',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: totalTimeSpentOnChallenges
            }
        },
        totalMinutesSpentOnWarmupChallenges:{
            'index': totalMinutesSpentOnWarmupChallenges,
            'name':'totalMinutesSpentOnWarmupChallenges',
            'displayName':'Total Minutes Spent on Warmup Challenges',
            'description':'The total minutes a student has spent on all warmup challenges',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalMinutesSpentOnWarmupChallenges
            },
        },
        totalMinutesSpentOnSeriousChallenges:{
            'index': totalMinutesSpentOnSeriousChallenges,
            'name':'totalMinutesSpentOnSeriousChallenges',
            'displayName':'Total Minutes Spent on Serious Challenges',
            'description':'The total minutes a student has spent on all serious challenges',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalMinutesSpentOnSeriousChallenges
            },
        },
        timeSpentOnQuestions:{
            'index': timeSpentOnQuestions,
            'name':'timeSpentOnQuestions',
            'displayName':'Time Spent On Questions (Minutes)',
            'description':'The total time in minutes a student has spent completing questions',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endQuestion], #I'm not sure this makes sense - Keith
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: totalTimeSpentOnQuestions
            }
        },
        differenceFromLastChallengeScore:{
            'index': differenceFromLastChallengeScore,
            'name':'differenceFromLastChallengeScore',
            'displayName':'Score Difference from Last Completed Challenge',
            'description':'The student score difference from the last completed challenge and a particular challenge',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getConsecutiveScoresDifference
            },
        },
        consecutiveDaysLoggedIn:{
            'index':consecutiveDaysLoggedIn,
            'name':'consecutiveDaysLoggedIn',
            'displayName':'Consecutive Days Logged In',
            'description':'The number of consecutive days a student has logged in',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none: [Event.userLogin],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: getConsecutiveDaysLoggedIn
            }
        },                  
        consecutiveDaysWarmUpChallengesTaken30Percent:{
            'index': consecutiveDaysWarmUpChallengesTaken30Percent,
            'name':'consecutiveDaysWarmUpChallengesTaken30Percent',
            'displayName':'Consecutive Days Warm Up Challenge Taken (at least 30% correct)',
            'description':'The number of consecutive days an student has taken a particular warm-up challenge with at least 30% correct.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge , Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getConsecutiveDaysWarmUpChallengesTaken30Percent
            }
        },
        consecutiveDaysWarmUpChallengesTaken75Percent:{
            'index': consecutiveDaysWarmUpChallengesTaken75Percent,
            'name':'consecutiveDaysWarmUpChallengesTaken75Percent',
            'displayName':'Consecutive Days Warm Up Challenge Taken (at least 75% correct)',
            'description':'The number of consecutive days an student has taken a particular warm-up challenge with at least 75% correct.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getConsecutiveDaysWarmUpChallengesTaken75Percent
            }
        },
        numDaysSubmissionEarlier:{
            'index': numDaysSubmissionEarlier,
            'name':'numDaysSubmissionEarlier',
            'displayName':'Number of Days Submission Earlier',
            'description':'The number of days an student submission is turned in earlier than the stated deadline',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge],
                ObjectTypes.activity: [Event.activitySubmission],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: calcNumDaysSubmissionEarly,
                ObjectTypes.activity: getNumDaysSubmissionEarlyActivity
            }
        },
        numDaysSubmissionLate:{
            'index': numDaysSubmissionLate,
            'name':'numDaysSubmissionLate',
            'displayName':'Number of Days Submission Late',
            'description':'The number of days an student submission is turned in later than the stated deadline',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge],
                ObjectTypes.activity: [Event.activitySubmission],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: calcNumDaysSubmissionLate,
                ObjectTypes.activity: getNumDaysSubmissionLateActivity,
            } 
        },
        numAttempts:{
            'index': numAttempts,
            'name':'numAttempts',
            'displayName':'Number of Attempts',
            'description':'The number of times a student has completed a challenge',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.startChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getNumAttempts
            }
        },
        activitiesCompleted:{
            'index':activitiesCompleted,
            'name':'activitiesCompleted',
            'displayName':'Number of Activities Participated',
            'description':'The number of activities a student has received participation',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: getActivitiesCompleted
            }
        },
        badgesEarned:{
            'index': badgesEarned,
            'name':'badgesEarned',
            'displayName':'Badges Earned',
            'description':'The number of badges the student has earned',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.badgeEarned, Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfBadgesEarned
            },
        }, 
        uniqueSeriousChallengesAttempted:{
            'index': uniqueSeriousChallengesAttempted,
            'name':'uniqueSeriousChallengesAttempted',
            'displayName':'Unique Serious Challenges Completed',
            'description':'The number of serious challenges that a student has attempted at least once.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesAttempted
            },
        },
        uniqueWarmupChallengesAttempted:{
            'index': uniqueWarmupChallengesAttempted,
            'name':'uniqueWarmupChallengesAttempted',
            'displayName':'Unique Warmup Challenges Completed',
            'description':'The number of warmup challenges that a student has attempted at least once.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesAttempted
            },
        },   
        uniqueWarmupChallengesGreaterThan30Percent:{
            'index': uniqueWarmupChallengesGreaterThan30Percent,
            'name':'uniqueWarmupChallengesGreaterThan30Percent',
            'displayName':'Warmup Challenges Score (greater than 30% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than 30%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan30Percent
            },
        },
        uniqueWarmupChallengesGreaterThan75Percent:{
            'index': uniqueWarmupChallengesGreaterThan75Percent,
            'name':'uniqueWarmupChallengesGreaterThan75Percent',
            'displayName':'Warmup Challenges Score (greater than 75% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than 75%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan75Percent
            },
        },
        uniqueWarmupChallengesGreaterThan90Percent:{
            'index': uniqueWarmupChallengesGreaterThan90Percent,
            'name':'uniqueWarmupChallengesGreaterThan90Percent',
            'displayName':'Warmup Challenges Score (greater than 90% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than 90%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan90Percent
            },
        },
        uniqueSeriousChallengesGreaterThan30Percent:{
            'index': uniqueSeriousChallengesGreaterThan30Percent,
            'name':'uniqueSeriousChallengesGreaterThan30Percent',
            'displayName':'Serious Challenges Score (greater than 30% correct)',
            'description':'The number of serious challenges a student has completed with a score greater than 30%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesGreaterThan30Percent
            },
        },
        uniqueSeriousChallengesGreaterThan75Percent:{
            'index': uniqueSeriousChallengesGreaterThan75Percent,
            'name':'uniqueSeriousChallengesGreaterThan75Percent',
            'displayName':'Serious Challenges Score (greater than 75% correct)',
            'description':'The number of serious challenges a student has completed with a score greater than 75%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesGreaterThan75Percent
            },
        },
        uniqueSeriousChallengesGreaterThan90Percent:{
            'index': uniqueSeriousChallengesGreaterThan90Percent,
            'name':'uniqueSeriousChallengesGreaterThan90Percent',
            'displayName':'Serious Challenges Score (greater than 90% correct)',
            'description':'The number of serious challenges a student has completed with a score greater than 90%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesGreaterThan90Percent
            },
        },
        uniqueWarmupChallengesGreaterThan75PercentForTopic:{
            'index': uniqueWarmupChallengesGreaterThan75PercentForTopic,
            'name':'uniqueWarmupChallengesGreaterThan75PercentForTopic',
            'displayName':'Warmup Challenges Score for Specific Topic (greater than 75% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than 75% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic
            },
        },  
        uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt:{
            'index': uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt,
            'name':'uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt',
            'displayName':'One Attempt Warmup Challenges Score (greater than 75% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than 75% and with only one attempt',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt
            },
        },  
        duelsSent:{
            'index': duelsSent,
            'name':'duelsSent',
            'displayName':'# of Duels Sent',
            'description':'The total number of duels a student has sent to other students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.duelSent],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfDuelsSent
            },
        },  
        duelsAccepted:{
            'index': duelsAccepted,
            'name':'duelsAccepted',
            'displayName':'# of Duels Accepted',
            'description':'The total number of duels a student has accepted from other students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.duelAccepted],  
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfDuelsAccepted
            },
        },     
        duelsWon:{
            'index': duelsWon,
            'name':'duelsWon',
            'displayName':'# of Duels Won',
            'description':'The total number of duels a student has won',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.duelWon],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfDuelsWon
            },
        },       
        duelsParticipated:{
            'index': duelsParticipated,
            'name':'duelsParticipated',
            'displayName':'# of Duels Participation',
            'description':'The total number of duels a student has participated in regarless of the duels outcomes',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.duelWon, Event.duelLost],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfDuelsParticipated
            },
        },   
        duelsLost:{
            'index': duelsLost,
            'name':'duelsLost',
            'displayName':'# of Duels Lost',
            'description':'The total number of duels a student has lost',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.duelLost],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfDuelsLost
            },
        },   
        calloutSent:{
            'index': calloutSent,
            'name':'calloutSent',
            'displayName':'# of Call Outs Sent',
            'description':'The total number of call outs a student has sent to other students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.calloutSent],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfCalloutSent
            },
        },  
        calloutParticipate:{
            'index': calloutParticipate,
            'name':'calloutParticipate',
            'displayName':'# of Call Outs Participation',
            'description':'The total number of call outs a student has participated in weather they won or not',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.calloutWon, Event.calloutLost],  
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfCalloutParticipate
            },
        },     
        calloutParticipationWon:{
            'index': calloutParticipationWon,
            'name':'calloutParticipationWon',
            'displayName':'# of Call Outs a participant has won',
            'description':'The total number of calls out a student has won',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.calloutWon],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfCalloutParticipationWon
            },
        },    
        calloutParticipationLost:{
            'index': calloutParticipationLost,
            'name':'calloutParticipationLost',
            'displayName':'# of Call Outs a participant has lost',
            'description':'The total number of call outs a student has lost',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.calloutLost],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfCalloutParticipationLost
            },
        },   
        calloutRequested:{
            'index': calloutRequested,
            'name':'calloutRequested',
            'displayName':'# of Call Outs a participant has been reqeusted',
            'description':'The total number of call outs a student has been requested',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.calloutRequested],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfCalloutRequested
            },
        },                                                                  
    }

if __debug__:
    # Check for mistakes in the systemVariables enum, such as duplicate
    # id numbers or mismatches between eventsWhichCanChangeThis and functions
    expectedFieldsInSysVarStruct = ['index','name','displayName','description','eventsWhichCanChangeThis','type','functions']
    
    sysVarNames = [sv for sv in SystemVariable.__dict__ if sv[:1] != '_' and sv != 'systemVariables']
    sysVarNumSet = set()
    for sysVarName in sysVarNames:
        sysVarNum = SystemVariable.__dict__[sysVarName]
        sysVarNumSet.add(sysVarNum)
        assert sysVarNum in SystemVariable.systemVariables, "System variable number created without corresponding structure in systemVariables dictionary.  %s = %i " % (sysVarName,sysVarNum)
        dictEntry = SystemVariable.systemVariables[sysVarNum]
        for field in expectedFieldsInSysVarStruct:
            assert field in dictEntry, "System variable structure missing expected field.  %s missing %s" % (sysVarName,field)
        eventsList = list(dictEntry['eventsWhichCanChangeThis'])
        functionsList = list(dictEntry['functions'])
        assert len([obj for obj in eventsList if obj not in functionsList]) == 0, "System variable structure has an event entry for an object type for which it has no function. %s " % sysVarName
        assert len([obj for obj in functionsList if obj not in eventsList]) == 0, "System variable structure has a functions entry for an object type for which it has no events entry. %s " % sysVarName
        if ObjectTypes.none in eventsList:
            assert len(eventsList) == 1, "System Variable structure has an object which attempts to be in both the global scope (ObjectTypes.none) and one or more specific object scope.  This is not allowed. %s " % sysVarName 

    assert len(sysVarNames) == len(sysVarNumSet), "Two system variables have the same number."
