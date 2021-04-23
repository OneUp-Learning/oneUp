import logging
from datetime import datetime

from Badges.enums import Event, ObjectTypes
from Instructors.constants import unlimited_constant
from Instructors.models import (Activities, ActivitiesCategory, Challenges,
                                ChallengesTopics, Questions, Topics, Skills)
from Instructors.views.utils import current_utctime
from django.db.models import Sum

logger = logging.getLogger(__name__)
objectTypeToObjectClass = {
    ObjectTypes.activity: Activities,
    ObjectTypes.challenge: Challenges,
    ObjectTypes.question: Questions,
    ObjectTypes.topic: Topics,
    ObjectTypes.activityCategory: ActivitiesCategory,
    ObjectTypes.skill: Skills,
}
    
# This is where we evaluate the system variables in their appropriate
# context.
def calculate_system_variable(varIndex,course,student,objectType,objectID):
    print("Calculating SystemVariable: VarIndex: " + str(varIndex) + " VarName: "+SystemVariable.systemVariables[varIndex]["name"]+ " ObjType:"+ 
        str(objectType)+" ObjectID: "+str(objectID))
    
    systemVar = SystemVariable.systemVariables[varIndex]
    functions = systemVar["functions"]

    if ObjectTypes.none in functions:
        return functions[ObjectTypes.none](course,student)
    else:
        if objectType not in functions:
            return "Error: no function defined to calculate this system variable for the specified object type (or no function defined to calculate it at all)!"
        dbobject = objectTypeToObjectClass[objectType].objects.get(pk=objectID)
        return functions[objectType](course,student,dbobject)


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

def getUniqueChallengesGreaterThanPercentage(course, student, isGraded, percentage, topic=None):
    ''' Utility function used by other functions.
        Returns the number of challenges greater than or equal to some percentage.
        isGraded when True is serious
        isGraded when False is warmup
        function will check for a specific topic if topic is passed
    '''
    challengesGreaterThan = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=isGraded)
    for challenge in challenges:
        if topic:
            challengeTopics = ChallengesTopics.objects.filter(topicID=topic, challengeID = challenge.challengeID)
            if challengeTopics.exists():
                # Get the highest percentage correct from challenge. Also checks to see if student has taken that challenge
                percent_of_max_score = getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge)
                if percent_of_max_score >= percentage:
                    challengesGreaterThan += 1
        else:
            # Get the highest percentage correct from challenge. Also checks to see if student has taken that challenge
            percent_of_max_score = getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge)
            if percent_of_max_score >= percentage:
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
    now = current_utctime()
    diff = deadline-now
    return diff.days

def challengesForTopic(course,topic):
    challengesTopics = ChallengesTopics.objects.filter(topicID = topic,challengeID__courseID=course)
    challenges_in_topic = [ct.challengeID for ct in challengesTopics]
    return challenges_in_topic

def getTimeSpentOnChallenges(course, student, isGraded, topic=None):
    ''' Utility function used by other functions.
        Returns the total time in minutes a student has spent on challenges.
        isGraded when True is serious
        isGraded when False is warmup
    '''
    from Students.models import StudentChallenges
    # This calculates the time for both serious and warmup challenges
    #return the sum of delta times between StartChallenge and End Challenge events   
    challengeTimes = StudentChallenges.objects.filter(courseID = course,studentID = student, challengeID__isGraded=isGraded).exclude(endTimestamp__isnull=True) #ensure that the challenge has an endTimestamp
    if topic:
        from Instructors.models import ChallengesTopics
        challengeTimes = challengeTimes.filter(challengeID__in=challengesForTopic(course,topic))
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

        NOTE: This will consider all challenge attempts including if the challenge is no longer available
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

def topicScore(course, student, topic):
    from Students.models import StudentChallenges
    attempts = StudentChallenges.objects.filter(studentID=student,courseID=course,challengeID__in=challengesForTopic(course, topic))
    attempts_by_challenge = {attempt.challengeID_id:[] for attempt in attempts}
    for attempt in attempts:
        attempts_by_challenge[attempt.challengeID_id].append(attempt.getScore())
    best_scores = [max(scores) for attempt,scores in attempts_by_challenge.items()]
    return sum(best_scores)

def topicPercentOfScoreOutOfMaxChallengeScore(course, student, topic):
    student_total = topicScore(course,student,topic)
    challenges = challengesForTopic(course, topic)
    possible_score = sum([challenge.getCombinedScore() for challenge in challenges])
    if possible_score == 0:
        possible_score = 0.00001;
        # Avoid division by 0 in case there are no points
    return student_total/possible_score*100

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

def getSumOfScoreOfEveryStudentActivity(course,student, activity):
    ''' Return the sum of every student's score of an activity for a course'''
    scores = getAllActivityScores(course, activity)
    if len(scores) == 0:
        return 0
    return float(sum([score.activityScore for score in scores]))

def getSumOfScoreOfAllStudentActivitiesCategory(course, student, category):
    ''' Return the sum of student's activities for a particular category'''
    #print("coooom here")
    #print(category)
    from Students.models import StudentActivities
    StudActivities = StudentActivities.objects.filter(courseID=course, studentID=student, activityID__category=category)
    if len(StudActivities) == 0:
        return 0
    #print(float(sum([StudActivity.activityScore for StudActivity in StudActivities])))
    return float(sum([StudActivity.activityScore for StudActivity in StudActivities]))

def getMinScoreOfStudentsActivitiesCategory(course, student, category):
    ''' Return the min score out of all students' activities for a particular category. this functions sums
    every student's activies in a particular categroy and returns the lowest '''
    from Students.models import StudentRegisteredCourses
    students = StudentRegisteredCourses.objects.filter(courseID = course).exclude(studentID__isTestStudent=True)
    scores = [getSumOfScoreOfAllStudentActivitiesCategory(course, student.studentID, category) for student in students]
    return float(min(scores))

def getMaxScoreOfStudentsActivitiesCategory(course, student, category):
    ''' Return the max score out of all students' activities for a particular category. this functions sums
    every student's activies in a particular categroy and returns the highest '''
    from Students.models import StudentRegisteredCourses
    students = StudentRegisteredCourses.objects.filter(courseID = course).exclude(studentID__isTestStudent=True)
    scores = [getSumOfScoreOfAllStudentActivitiesCategory(course, student.studentID, category) for student in students]
    return float(max(scores))

def getAveOfScore(course, student, category):
    
    print("coooom here")
    print(category)
    from Students.models import StudentActivities
    StudActivities = StudentActivities.objects.filter(courseID=course, studentID=student, activityID__category=category)
    if len(StudActivities) == 0:
        return 0
    return float(sum([StudActivity.activityScore for StudActivity in StudActivities])/len(StudActivities))

def getAverageScoreOfStudentsActivitiesCategory(course, student, category):
    ''' Return the average score of all students' activities for a particular category. this functions sums
    every student's activies in a particular categroy and returns the average '''
    from Students.models import StudentRegisteredCourses
    print("at least here")
    students = StudentRegisteredCourses.objects.filter(courseID = course).exclude(studentID__isTestStudent=True)
    scores = [getAveOfScore(course, student.studentID, category) for student in students]
    if not scores:
        return 0
    print(scores)
    print("getAverageScoreOfStudentsActivitiesCategory")
    print(float(sum(scores)/len(scores)))
    return float(sum(scores)/len(scores))

def getSumOfScoreOfAllStudentsActivitiesCategory(course, student, category):
    ''' Return the sum of every student's activities for a particular category'''
    from Students.models import StudentRegisteredCourses
    students = StudentRegisteredCourses.objects.filter(courseID = course)
    scores = [getSumOfScoreOfAllStudentActivitiesCategory(course, student.studentID, category) for student in students]
    return float(sum(scores))

def getPercentOfScoreOutOfMaxChallengeScore(course, student, challenge):
    ''' This will return the percentage of the highest challenge score obtained by a student
        for a challenge.
        Score includes score + adjustment + curve (bonus points not included)
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

def getPercentOfFirstAttemptScoreOutOfChallengeScore(course, student, challenge):
    ''' This will return the percentage of the first attempted challenge score obtained by a student
        for a challenge.
        Score includes score + adjustment + curve (bonus points not included)
    '''
    first_attempt = getTestScores(course,student,challenge).order_by('endTimestamp').first()
    challenge_score = challenge.getCombinedScore()
    percentage = 0

    if first_attempt and challenge_score != 0:
        score = first_attempt.getScore()
        percentage = float(score)/float(challenge_score) * 100

    return percentage

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
    return not serious_challenge.hasDueDate or (serious_challenge.hasDueDate and current_utctime().replace(microsecond=0) >= serious_challenge.dueDate.replace(microsecond=0))

def isWarmUpChallenge(course,student,challenge):
    ''' This will return True/False if the a particular challenge is a warmup challenge'''
    return not challenge.isGraded

def totalTimeSpentOnChallenges(course,student,topic=None):
    ''' This will return the total minutes a student has spent completing any challenges'''
    return getTimeSpentOnChallenges(course, student, True,topic) + getTimeSpentOnChallenges(course, student, False,topic)

def getTotalMinutesSpentOnWarmupChallenges(course, student, topic = None):
    ''' This will return the number of minutes a student has spent on all warmup challenges'''    
    minutes = getTimeSpentOnChallenges(course, student, False, topic)
    logger.debug("Total minutes spent on warmup challenges: " + str(minutes))
    return minutes

def getTotalMinutesSpentOnSeriousChallenges(course, student, topic = None):
    ''' This will return the number of minutes a student has spent on all serious challenges'''    
    minutes = getTimeSpentOnChallenges(course, student, True, topic)
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
    dates = list(map(lambda d: d['timestamp'].toordinal(),studentEventDates))
    
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
                print("Time : ", event.timestamp)
                warmUpChallDates.append(event.timestamp)  
    # get today's date in utc            
    today = current_utctime().date()
    
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
                print("Time : ", event.timestamp)
                warmUpChallDates.append(event.timestamp)  
    # get today's date in utc            
    today = current_utctime().date()
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
    from Badges.models import BadgesInfo
    course_badges = BadgesInfo.objects.filter(courseID=course)
    badges_total = 0
    for course_badge in course_badges:
        student_badges = StudentBadges.objects.filter(badgeID=course_badge, studentID=student)
        badges_total += student_badges.count()
        
    logger.debug("Number of Earned Badges by student: " + str(badges_total))
    return badges_total

def getDuelChallenges(course,topic=None):
    from Students.models import DuelChallenges
    result = DuelChallenges.objects.filter(courseID=course)
    if topic:
        result = result.filter(challengeID__in = challengesForTopic(course,topic))
    return result

def getNumberOfDuelsSent(course, student, topic=None):
    ''' This will return the number of duels sent by a student regardless of the
        outcome of the duel
    '''
    sent = getDuelChallenges(course,topic).filter(challenger=student).count()
    return sent

def getNumberOfDuelsAccepted(course, student, topic=None):
    ''' This will return the number of duels a student has accepted sent by any other
        student.
        Status -> indicates the status of the challenge 0=canceled ,1=pending, 2=accepted
    '''
    accepted = getDuelChallenges(course,topic).filter(challengee=student, status=2).count()
    return accepted

def getNumberOfDuelsWon(course, student, topic=None):
    ''' This will return the number of wins the student has earned for every duel 
        in the course
    '''
    from Students.models import Winners
    wins = Winners.objects.filter(studentID=student, courseID=course)
    if topic:
        wins = wins.filter(DuelChallengeID__challengeID__in=challengesForTopic(course,topic))
    return wins.count()

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
    sent = DuelChallenges.objects.filter(challenger=student, courseID=course, status=2).count()
    received = DuelChallenges.objects.filter(challengee=student, courseID=course, status=2).count()
    total_duels = sent+received
    duel_wins = Winners.objects.filter(studentID=student, courseID=course).count()
    duel_losses = total_duels - duel_wins
    return duel_losses
    ''' Previous code that was incorrect
    duel_challenges = DuelChallenges.objects.filter(challenger=student, courseID=course)
    duel_wins = Winners.objects.filter(studentID=student, courseID=course)
    
    count = 0
    for duel_win in duel_wins:
        if duel_win.DuelChallengeID in duel_challenges:
            count += 1

    return count'''

def getCallouts(course,topic=None):
    from Students.models import Callouts
    callouts = Callouts.objects.filter(courseID=course)
    if topic:
        callouts = callouts.filter(challengeID__in = challengesForTopic(course,topic))
    return callouts

def getNumberOfCalloutSent(course, student, topic=None):
    ''' This will return the number of call outs sent by a student regardless of weather sender won or not
    '''
    sent = getCallouts(course,topic).filter(sender=student).count()
    return sent

def getNumberOfCalloutParticipate(course, student, topic=None):
    ''' This will return the number of call outs a student has participated in sent by any other
        student regardless of weather participant won or not.
    '''
    from Students.models import CalloutStats
    calloutstats = CalloutStats.objects.filter(studentID=student, courseID=course)
    if topic:
        calloutstats = calloutstats.filter(calloutID__challengeID__in=challengesForTopic(course,topic))
    return calloutstats.count()

def getCalloutParticipants(course, student, topic=None):
    from Students.models import CalloutParticipants
    callouts = CalloutParticipants.objects.filter(courseID=course, participantID=student)
    if topic:
        callouts = callouts.filter(calloutID__challengeID__in = challengesForTopic(course,topic))
    return callouts 

def getNumberOfCalloutRequested(course, student, topic=None):
    ''' This will return the number of call outs a student has been requested, sent by any other
        student regardless of weather participant won or not.
    '''
    return getCalloutParticipants(course, student, topic).count()

def getNumberOfCalloutParticipationWon(course, student, topic=None):
    ''' This will return the number of wins the student has earned for every requested call out 
        in the course 
    '''
    return getCalloutParticipants(course, student, topic).filter(hasWon=True).count()

def getNumberOfCalloutParticipationLost(course, student, topic=None):
    ''' This will return the number of lost the student has for every requested call out 
        in the course 
    '''
    return getCalloutParticipants(course, student, topic).filter(hasWon=False, hasSubmitted=True).count()

def getNumberOfUniqueSeriousChallengesAttempted(course, student,topic=None):
    ''' Get the number of unique serious challenges the student has taken.'''    
    challenges = Challenges.objects.filter(courseID=course, isGraded=True)
    if topic:
        challenges = challenges.filter(challengeID__in=challengesForTopic(course,topic))
    attempted = 0
    for challenge in challenges:
        studentChallenges = getNumAttempts(course, student, challenge)
        if studentChallenges > 0:
            attempted += 1
    
    logger.debug("Serious Challenges Attempted: " + str(attempted))
    return attempted

def getNumberOfUniqueWarmupChallengesAttempted(course, student):
    ''' Get the number of warmup challenges the student has taken (score > 0).'''  
    from Students.models import StudentChallenges  
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    attempted = 0
    for challenge in challenges:
        #flag for checking if the student has submission greater than zero.
        gradeMoreThanZero=False
        challengeAttempts = StudentChallenges.objects.filter(courseID=course, studentID=student,challengeID=challenge)
        if challengeAttempts.exists():
            #iterates through all attempts checking for one > 0
            for attempt in challengeAttempts:
#                print("****************************"+str(attempt.testScore))
                if attempt.testScore > 0:
                    gradeMoreThanZero=True
            if gradeMoreThanZero:
                attempted += 1
    logger.debug("Warmup Challenges Attempted: " + str(attempted))
    return attempted
            
def getNumberOfUniqueSeriousChallengesGreaterThan30Percent(course, student):  
    ''' This will return the number of unique serious challenges that a student completed with a 
        score >= 30%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, True, 30.0)
    logger.debug("Number of unqiue serious challenges >= 30%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueSeriousChallengesGreaterThan75Percent(course, student):  
    ''' This will return the number of unique serious challenges that a student completed with a 
        score >= 75%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, True, 75.0)
    logger.debug("Number of unqiue serious challenges >= 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueSeriousChallengesGreaterThan90Percent(course, student):  
    ''' This will return the number of unique serious challenges that a student completed with a 
        score >= 90%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, True, 90.0)
    logger.debug("Number of unqiue serious challenges >= 90%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan60Percent(course, student):  
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 60%
    '''  
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 60.0)
    logger.debug("Number of unique warmup challenges >= 60%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan75Percent(course, student): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 75%
    '''   
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 75.0)
    logger.debug("Number of unique warmup challenges >= 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan80Percent(course, student): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 80%
    '''   
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 80.0)
    logger.debug("Number of unique warmup challenges >= 80%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreaterThan90Percent(course, student):  
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 90%
    '''
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 90.0)
    logger.debug("Number of unique warmup challenges >= 90%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic(course, student, topic): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 75% for a particular topic
    '''
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 75.0, topic=topic)
    logger.debug("Number of unqiue warmup challenges with specific topic >= 75%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreater70PercentPerTopic(course, student, topic): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 70% for a particular topic
    '''
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 70.0, topic=topic)
    logger.debug("Number of unqiue warmup challenges with specific topic >= 70%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreater85PercentPerTopic(course, student, topic): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 85% for a particular topic
    '''
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 85.0, topic=topic)
    logger.debug("Number of unqiue warmup challenges with specific topic >= 85%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def getNumberOfUniqueWarmupChallengesGreater90PercentPerTopic(course, student, topic): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 90% for a particular topic
    '''
    challengesGreaterThan = getUniqueChallengesGreaterThanPercentage(course, student, False, 90.0, topic=topic)
    logger.debug("Number of unqiue warmup challenges with specific topic >= 90%: " + str(challengesGreaterThan))
    return challengesGreaterThan

def topicPercentageHelper(f,course,student,topic):
    return f(course,student,topic)/len(challengesForTopic(course,topic))*100

def getPercentageOfUniqueWarmupChallengesGreater70PercentPerTopic(course, student, topic):
    return topicPercentageHelper(getNumberOfUniqueWarmupChallengesGreater70PercentPerTopic,course, student, topic)

def getPercentageOfUniqueWarmupChallengesGreater75PercentPerTopic(course, student, topic):
    return topicPercentageHelper(getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic,course, student, topic)

def getPercentageOfUniqueWarmupChallengesGreater85PercentPerTopic(course, student, topic):
    return topicPercentageHelper(getNumberOfUniqueWarmupChallengesGreater85PercentPerTopic,course, student, topic)

def getPercentageOfUniqueWarmupChallengesGreater90PercentPerTopic(course, student, topic):
    return topicPercentageHelper(getNumberOfUniqueWarmupChallengesGreater90PercentPerTopic,course, student, topic)

def allWarmupChallengesTopicGreaterThan70Percent(course, student, topic): 
    ''' This will return the 1 (true) or 0 (false) if every challenge related to the given topic is greater than 70%'''
   
    from Instructors.models import ChallengesTopics 
    from Students.models import StudentChallenges 
    challengesTopics = ChallengesTopics.objects.filter(topicID=topic,challengeID__courseID=course)
    for challsTopic in challengesTopics:
        if challsTopic.challengeID.isGraded == True:
            continue
        if StudentChallenges.objects.filter(studentID = student, challengeID = challsTopic.challengeID, challengeID__isGraded=False):
            percentage = (float(getPercentOfScoreOutOfMaxChallengeScore(course, student, challsTopic.challengeID)) / float(challsTopic.challengeID.totalScore)) * 100.0
            if percentage <= 70.0:
                return False
        else:
            return False
    logger.debug("All warmup challenges related to the given topic are greater than 70%")
    return True

def allWarmupChallengesTopicGreaterThan85Percent(course, student, topic): 
    ''' This will return the 1 (true) or 0 (false) if every challenge related to the given topic is greater than 85%'''
   
    from Instructors.models import ChallengesTopics 
    from Students.models import StudentChallenges 
    challengesTopics = ChallengesTopics.objects.filter(topicID=topic,challengeID__courseID=course)
    for challsTopic in challengesTopics:
        if challsTopic.challengeID.isGraded == True:
            continue
        if StudentChallenges.objects.filter(studentID = student, challengeID = challsTopic.challengeID, challengeID__isGraded=False):
            percentage = (float(getPercentOfScoreOutOfMaxChallengeScore(course, student, challsTopic.challengeID)) / float(challsTopic.challengeID.totalScore)) * 100.0
            if percentage <= 85.0:
                return False
        else:
            return False
    logger.debug("All warmup challenges related to the given topic are greater than 85%")
    return True

def getAveragePercentageOfWarmupsForTopic(course, student, topic): 
    ''' This will return the average percentage of warmups related to the given topic'''
   
    from Instructors.models import ChallengesTopics 
    from Students.models import StudentChallenges 
    challengesTopics = ChallengesTopics.objects.filter(topicID=topic,challengeID__courseID=course)
    percentage = 0.0
    count = 0.0
    for challsTopic in challengesTopics:
        if challsTopic.challengeID.isGraded == True:
            continue
        if StudentChallenges.objects.filter(studentID = student, challengeID = challsTopic.challengeID, challengeID__isGraded=False):
            percentage += getPercentOfScoreOutOfMaxChallengeScore(course, student, challsTopic.challengeID)
            count += 1.0
    # Prevent divide by zero
    count = max(1.0, count)

    logger.debug("The average percentage is" + str(percentage / count))
    return (percentage / count)

def getEarnedVCTotal(course, student):
    '''This will return the amount of vc a student has earned in total'''

    from Students.models import StudentVirtualCurrency

    student_vc = StudentVirtualCurrency.objects.filter(studentID = student, courseID = course)
    return sum([int(vc.value) for vc in student_vc if vc.value > 0])

def getSpentVCTotal(course, student):
    '''This will return the amount of vc a student has spent in total'''

    from Students.models import StudentVirtualCurrencyTransactions

    student_spent_vc = StudentVirtualCurrencyTransactions.objects.filter(student = student, course = course).filter(studentEvent__event=Event.spendingVirtualCurrency)
    return sum([int(vc.amount) for vc in student_spent_vc])

def getNumberOfUniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt(course, student): 
    ''' This will return the number of unique warmup challenges that a student completed with a 
        score >= 75% that the student has only completed once
    '''   
    numberOfChall = 0
    challenges = Challenges.objects.filter(courseID=course, isGraded=False)
    for challenge in challenges:
        allScores = getTestScores(course,student,challenge)
        if len(allScores)==1:
            percentage = getScorePercentage(course, student, challenge)
            if percentage >= 75:
                numberOfChall += 1
    print("Number of unqiue warmup challenges >= 75%: ", numberOfChall)
    return numberOfChall

def getStudentXP(course, student):
    from Students.models import StudentRegisteredCourses
    return float(StudentRegisteredCourses.objects.get(courseID=course, studentID=student).xp)

def getStudentVC(course, student):
    from Students.models import StudentRegisteredCourses
    return float(StudentRegisteredCourses.objects.get(courseID=course, studentID=student).virtualCurrencyAmount)

def getTotalMinutesSpentOnFlashcards(course, student):
    from Students.models import StudentEventLog
    from bisect import bisect_left

    endCard = list(StudentEventLog.objects.filter(course_id=course, student_id=student, event=Event.submitFlashCard))
    startCard = list(StudentEventLog.objects.filter(course_id=course, student_id=student, event=Event.viewFlashCard))
    #initialize dict with start IDs as key and corresponding timestamps as value
    startDict = {x.objectID:[] for x in startCard}
    print("!!!!!!!!!!!!!!", startDict)
    for scard in startCard:
        startDict[scard.objectID].append(scard.timestamp)
    print("!!!!!!!!!!!!!!", startDict)   
    #initialize time
    timeTotal = datetime(2000,1,1,0,0,0)
    overMinute = 0
    for ecard in endCard:
        #bisect method inserts and finds the corresponding start time, the time of the view event right before it
        startTimes = startDict[ecard.objectID]
        i = bisect_left(startTimes,ecard.timestamp) 
        matchingStartTime=startTimes[i-1]
        #keep track and cap time spent on individual cards to 1 minute
        print("***", matchingStartTime,"&&&", ecard.timestamp)
        
        if  (ecard.timestamp - matchingStartTime).total_seconds() > 60:
            overMinute += 1
        else:
            timeTotal += ecard.timestamp - matchingStartTime
    #subtract out initialization
    timeTotal -= datetime(2000,1,1,0,0,0)
    #add in to the total the cards capped at 1 minute
    totalMinutesSpent = (overMinute*60 + timeTotal.total_seconds())/60
        
    return totalMinutesSpent        

def getTotalOfCompletedFlashcards(course, student):
    from Students.models import StudentEventLog
    totalCards = len(StudentEventLog.objects.filter(course_id=course, student_id=student, event=Event.submitFlashCard))
    return totalCards

def skillPoints(course, student, skill):
    from Students.models import StudentCourseSkills
    scs =  StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__courseID = course, studentChallengeQuestionID__studentChallengeID__studentID = student, skillID = skill)
    result = scs.aggregate(total_points=Sum('skillPoints'))['total_points']
    if result is None:
        return 0
    else:
        return result

def maxSkillPoints(course, student, skill):
    from Students.models import StudentCourseSkills
    scs =  StudentCourseSkills.objects.filter(studentChallengeQuestionID_studentChallengeID_courseID = course, skillID = skill)
    result = scs.values('studentChallengeQuestionID__studentChallengeID__studentID').annotate(total=Sum('skillPoints')).order_by('-total')[0]['total']
    if result is None:
        return 0
    else:
        return result

class SystemVariable():
    numAttempts = 901 # The total number of attempts that a student has given to a challenge
    score = 902 # The score for the challenge or activity
    maxScore = 904 # The maximum of the test scores of all the student's attempts for a particular challenge
    minScore = 905 # The minimum of the test scores of all the student's attempts for a particular challenge
    dateOfFirstChallengeSubmission = 906 # The date on which the student has submitted a particular challenge for the first time.
    timeSpentOnChallenges = 907 # Time spent on a particular challenge.
    timeSpentOnQuestions = 908 # Time spent on a particular question. INCOMPLETE
    consecutiveDaysLoggedIn = 909 # The number of consecutive days a student logs in to the One Up website
    activitiesCompleted = 910 # The number of activities a student has completed for a particular course
    numDaysSubmissionEarlier = 912 #Number of days an assignment is submitted earlier INCOMPLETE
    numDaysSubmissionLate = 913 #Number of days an assignment is submitted late INCOMPLETE
#    averageTestScore = 914  # Deprecated folded into averageScore
    consecutiveDaysWarmUpChallengesTaken30Percent = 917 #Consecutive days warm up challenges at least 30% correct are taken
    consecutiveDaysWarmUpChallengesTaken75Percent = 918 #Consecutive days warm up challenges at least 75% correct are taken
    percentage = 919  # percentage of student's score (for the max scored attempt ) out of the max possible challenge score
    uniqueSeriousChallengesAttempted = 920 # The number of unique serious challenges completed by the student
    uniqueWarmupChallengesGreaterThan60Percent = 921 # Number of warmup challenges with a score percentage equal or greater than 60%
    uniqueWarmupChallengesGreaterThan75Percent = 922 # Number of warmup challenges with a score percentage equal or greater than 75%
    uniqueWarmupChallengesGreaterThan75PercentForTopic = 923 # Number of warmup challenges with a score percentage equal or greater than 75% for a particular topic
    totalMinutesSpentOnWarmupChallenges = 924 # Total minutes spent on warmup challenges only
    differenceFromLastChallengeScore = 925 # Score difference from last complete challenge/warmup challenge and a specific challenge
    averageScore = 928  
    percentageOfCorrectAnswersPerChallengePerStudent = 931 #percentage of correctly answered questions out of all the questions
    isWarmUp = 932 # is a warm-up challenge
    scorePercentageDifferenceFromPreviousActivity = 934 # Difference between the percentages of the student's scores for this activity and the one preceding it'''      
    percentageOfActivityScore = 935 # Percentage of the student's score out of the max possible score for this activity
    percentageOfMaxActivityScore = 936 # Percentage of the highest score for the course out of the max possible score for this activity
    uniqueWarmupChallengesAttempted = 937 # The number of unique challenges completed by the student
    badgesEarned = 938 # Number of badges student as earned
    scoreDifferenceFromPreviousActivity = 939 # score difference from previous activity
    uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt = 940 #The number of warmup challenges with a score equal or greater than 75% with only one attempt.
    activityScoreDifferenceByCategory = 941
    totalScoreForSeriousChallenges = 942
    totalScoreForWarmupChallenges = 943    
    seriousChallengeReachedDueDate = 944 
    uniqueWarmupChallengesGreaterThan90Percent = 945 
    uniqueSeriousChallengesGreaterThan90Percent = 946 # Number of serious challenges with a score percentage equal or greater than 90%
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
    percentOfFirstAttemptScoreOutOfChallengeScore = 961  # percentage of student's score (for the first attempt ) out of the max possible score for a challenge
    uniqueWarmupChallengesGreaterThan80Percent = 962 # Number of warmup challenges with a score percentage equal or greater than 80%
    uniqueWarmupChallengesGreaterThan70PercentTopic = 963 # Number of warmup challenges related to a topic with a score percentage greater than 70%
    uniqueWarmupChallengesGreaterThan85PercentTopic = 964 # Number of warmup challenges related to a topic with a score percentage greater than 85%
    warmupChallengesTopicGreaterThan70Percent = 965
    warmupChallengesTopicGreaterThan85Percent = 966 
    averagePercentageOfWarmupsForTopic = 967 # Average percenage of all warmups related to the given topic
    totalEarndVC = 968 # Total amount of vc earned by a student
    totalSpentVC = 969 # Total amount of vc spent by a student
    sumOfScoreOfEveryStudentActivity = 970
#    sumOfScoreOfAllStudentActivitiesCategory = 971  Deprecated.  Folded into the score variable
#    minScoreOfStudentsActivitiesCategory = 972 Deprecated.  Folded into MinScore
#    maxScoreOfStudentsActivitiesCategory = 973 Deprecated.  Folded into MaxScore
#    averageScoreOfStudentsActivitiesCategory = 974 Deprecated.  Folded into AverageScore
    sumOfScoreOfAllStudentsActivitiesCategory = 975
    averageScoreOfStudentActivitiesCategory = 976
    studentXP = 977 # Returns the current amount of XP a student has
    studentVC = 978 # Returns the current amount of VC a student has
    uniqueWarmupChallengesGreaterThan90PercentTopic = 979 # Number of warmup challenges related to a topic with a score percentage greater than 90%
    totalMinutesSpentOnWarmupChallengesPerTopic = 980
    timeSpentOnFlashcards = 981
    totalFlashcardsCompleted = 982
    timeSpentOnChallengesPerTopic = 983
    uniqueSeriousChallengesAttemptedForTopic = 984
    totalMinutesSpentOnSeriousChallengesPerTopic = 986
    duelsSentPerTopic = 987
    duelsAcceptedPerTopic = 988
    duelsWonPerTopic = 989
    calloutSentPerTopic = 990
    calloutParticipatePerTopic = 991
    calloutParticipationWonPerTopic = 992
    calloutParticipationLostPerTopic = 993
    calloutRequestedPerTopic = 994
    percentageWarmupChallengesGreaterThan70PercentTopic = 995 # Percentage of warmup challenges related to a topic with a score percentage greater than 70%
    percentageWarmupChallengesGreaterThan75PercentTopic = 996 # Percentage of warmup challenges related to a topic with a score percentage greater than 75%
    percentageWarmupChallengesGreaterThan85PercentTopic = 997 # Percentage of warmup challenges related to a topic with a score percentage greater than 85%
    percentageWarmupChallengesGreaterThan90PercentTopic = 998 # Percentage of warmup challenges related to a topic with a score percentage greater than 90%

    systemVariables = {
        score:{
            'index': score,
            'name':'score',
            'displayName':'Score',
            'description':'The completed activity or challenge score by a student. The student activity score does not include bonus points. The student challenge score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[Event.endChallenge, Event.adjustment],
                ObjectTypes.activity:[Event.participationNoted,],
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
                ObjectTypes.activityCategory: [Event.participationNoted],
                ObjectTypes.skill: [Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: activityScore,
                ObjectTypes.challenge: challengeScore,
                ObjectTypes.topic: topicScore,
                ObjectTypes.activityCategory: getSumOfScoreOfAllStudentActivitiesCategory,
                ObjectTypes.skill: skillPoints,
            },
            'studentGoal': False,   
        },
        totalScoreForWarmupChallenges:{
            'index': totalScoreForWarmupChallenges,
            'name':'totalScoreForWarmupChallenges',
            'displayName':'Warmup Challenges Total Score',
            'description':'The student total score for all attempted warmup challenges. Takes the earned points only from the first attempt of each challenge for the static problems but the highest score for the dynamic problems',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalScoreForWarmupChallenges
            },
            'studentGoal': False,
        },
        totalScoreForSeriousChallenges:{
            'index': totalScoreForSeriousChallenges,
            'name':'totalScoreForSeriousChallenges',
            'displayName':'Serious Challenges Total Score',
            'description':'The student total score for all attempted serious challenges. Takes the earned points only from the first attempt of each challenge for the static problems but the highest score for the dynamic problems',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getTotalScoreForSeriousChallenges
            },
            'studentGoal': False,
        },
        maxScore:{
            'index': maxScore,
            'name':'maxScore',
            'displayName':'Highest Score amongst all Students',
            'description':"The highest score of all student submissions for a particular challenge or activity. The student activity score does not include bonus points. The student challenge score only includes the student score, adjustment, and curve.",
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[ Event.challengeExpiration, Event.adjustment],
                ObjectTypes.activity: [Event.participationNoted],
                ObjectTypes.activityCategory: [Event.participationNoted],
                ObjectTypes.skill: [Event.endChallenge]
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getMaxTestScore,
                ObjectTypes.activity: getMaxActivityScore,
                ObjectTypes.activityCategory: getMaxScoreOfStudentsActivitiesCategory,
                ObjectTypes.skill: maxSkillPoints,
            },
            'studentGoal': False,
        },
        minScore:{
            'index': minScore,
            'name':'minScore',
            'displayName':'Lowest Score amongst all Students',
            'description':"The lowest score of all student submissions for a particular challenge or activity. The student activity score does not include bonus points. The student challenge score only includes the student score, adjustment, and curve.",
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge:[ Event.challengeExpiration,Event.adjustment],
                ObjectTypes.activity: [Event.participationNoted],
                ObjectTypes.activityCategory: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getMinTestScore,
                ObjectTypes.activity: getMinActivityScore,
                ObjectTypes.activityCategory: getMinScoreOfStudentsActivitiesCategory
            },
            'studentGoal': False,
        },
        averageScore:{
            'index':averageScore,
            'name':'averageScore',
            'displayName':'Average Score',
            'description':'The average score of all students for this thing',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity: [Event.participationNoted],
                ObjectTypes.challenge:[Event.endChallenge,Event.adjustment],
                ObjectTypes.activityCategory: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: getAverageActivityScore,
                ObjectTypes.challenge:getAverageTestScore,
                ObjectTypes.activityCategory: getAverageScoreOfStudentsActivitiesCategory
            },
            'studentGoal': False,
        },
        sumOfScoreOfEveryStudentActivity:{
            'index':sumOfScoreOfEveryStudentActivity,
            'name':'sumOfScoreOfEveryStudentActivity',
            'displayName':"Total score for an activity for all students",
            'description':'The total score for an activity for all students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: getSumOfScoreOfEveryStudentActivity
            },
            'studentGoal': False,
        },
        averageScoreOfStudentActivitiesCategory:{
            'index':averageScoreOfStudentActivitiesCategory,
            'name':'averageScoreOfStudentActivitiesCategory',
            'displayName':"Average score for a category for a student",
            'description':'The average score for a category for a student',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activityCategory: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activityCategory: getAveOfScore
            },
            'studentGoal': False,
        },
        sumOfScoreOfAllStudentsActivitiesCategory:{
            'index':sumOfScoreOfAllStudentsActivitiesCategory,
            'name':'sumOfScoreOfAllStudentsActivitiesCategory',
            'displayName':"Total score for a category for all students",
            'description':'The total score for a category for all students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activityCategory: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activityCategory: getSumOfScoreOfAllStudentsActivitiesCategory
            },
            'studentGoal': False,
        },
        percentage:{
            'index': percentage,
            'name':'percentage',
            'displayName':"Percentage of Student's Score Out of Possible Score",
            'description':"The percentage of the student's score.  For challenges, the best attempt is used. The student score only includes the student score, adjustment, and curve, but not any bonus points they have bought.",
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge, Event.adjustment],
                ObjectTypes.topic: [Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge:getPercentOfScoreOutOfMaxChallengeScore,
                ObjectTypes.topic:topicPercentOfScoreOutOfMaxChallengeScore,
            },
            'studentGoal': False,
        },  
        percentOfFirstAttemptScoreOutOfChallengeScore:{
            'index': percentOfFirstAttemptScoreOutOfChallengeScore,
            'name':'percentOfFirstAttemptScoreOutOfChallengeScore',
            'displayName':'Percentage of Student First Attempt Score Out of Challenge Score',
            'description':'The percentage of the student first attempt score for a particular challenge. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getPercentOfFirstAttemptScoreOutOfChallengeScore
            },
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
        },
        activityScoreDifferenceByCategory:{
            'index': activityScoreDifferenceByCategory,
            'name':'activityScoreDifferenceByCategory',
            'displayName':'Score Difference From Averaged Previous Activities Scores For Activity Category',
            'description':'The student score difference from averaged previous activities scores based on a particular activity category',
            'eventsWhichCanChangeThis':{
                ObjectTypes.activity: [Event.participationNoted],
            },
            'type':'int',
            'functions':{
                ObjectTypes.activity: activityScoreDifferenceFromPreviousAveragedScoresByCategory
            },
            'studentGoal': False,
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
            },
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
        },
        timeSpentOnChallenges:{
            'index': timeSpentOnChallenges,
            'name':'timeSpentOnChallenges',
            'displayName':'Time Minutes Spent On Challenges',
            'description':'The total time in minutes a student has spent completing both warmup and serious challenges',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: totalTimeSpentOnChallenges
            },
            'studentGoal': False,
        },
        timeSpentOnChallengesPerTopic:{
            'index': timeSpentOnChallengesPerTopic,
            'name':'timeSpentOnChallengesPerTopic',
            'displayName':'Time Minutes Spent On Challenges',
            'description':'The total time in minutes a student has spent completing both warmup and serious challenges in a particular topic',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic: totalTimeSpentOnChallenges
            },
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
        },
        totalMinutesSpentOnWarmupChallengesPerTopic:{
            'index': totalMinutesSpentOnWarmupChallengesPerTopic,
            'name':'totalMinutesSpentOnWarmupChallengesPerTopic',
            'displayName':'Total Minutes Spent on Warmup Challenges Per Topic',
            'description':'The total minutes a student has spent on warmup challenges in a topic',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getTotalMinutesSpentOnWarmupChallenges
            },
            'studentGoal': False,
        },
        totalMinutesSpentOnSeriousChallengesPerTopic:{
            'index': totalMinutesSpentOnSeriousChallengesPerTopic,
            'name':'totalMinutesSpentOnSeriousChallengesPerTopic',
            'displayName':'Total Minutes Spent on Serious Challenges Per Topic',
            'description':'The total minutes a student has spent on serious challenges in a topic',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getTotalMinutesSpentOnSeriousChallenges
            },
            'studentGoal': False,
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
            },
            'studentGoal': False,
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
            'studentGoal': False,
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
            },
            'studentGoal': True,
        },                  
        consecutiveDaysWarmUpChallengesTaken30Percent:{
            'index': consecutiveDaysWarmUpChallengesTaken30Percent,
            'name':'consecutiveDaysWarmUpChallengesTaken30Percent',
            'displayName':'Consecutive Days Warm Up Challenge Taken (>= 30% correct)',
            'description':'The number of consecutive days an student has taken a particular warm-up challenge with at least 30% correct.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge , Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getConsecutiveDaysWarmUpChallengesTaken30Percent
            },
            'studentGoal': False,
        },
        consecutiveDaysWarmUpChallengesTaken75Percent:{
            'index': consecutiveDaysWarmUpChallengesTaken75Percent,
            'name':'consecutiveDaysWarmUpChallengesTaken75Percent',
            'displayName':'Consecutive Days Warm Up Challenge Taken (>= 75% correct)',
            'description':'The number of consecutive days an student has taken a particular warm-up challenge with at least 75% correct.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.challenge: [Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.challenge: getConsecutiveDaysWarmUpChallengesTaken75Percent
            },
            'studentGoal': False,
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
            },
            'studentGoal': False,
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
            },
            'studentGoal': False,
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
            },
            'studentGoal': False,
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
            },
            'studentGoal': False,
        },
        badgesEarned:{
            'index': badgesEarned,
            'name':'badgesEarned',
            'displayName':'Badges Earned',
            'description':'The number of badges the student has earned',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.badgeEarned],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfBadgesEarned
            },
            'studentGoal': True,
        }, 
        uniqueSeriousChallengesAttempted:{
            'index': uniqueSeriousChallengesAttempted,
            'name':'uniqueSeriousChallengesAttempted',
            'displayName':'# of Unique Serious Challenges Completed',
            'description':'The number of serious challenges that a student has attempted at least once with a score > 0.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesAttempted
            },
            'studentGoal': False,
        },
        uniqueSeriousChallengesAttemptedForTopic:{
            'index': uniqueSeriousChallengesAttemptedForTopic,
            'name':'uniqueSeriousChallengesAttemptedForTopic',
            'displayName':'# of Unique Serious Challenges Completed Per Topic',
            'description':'The number of serious challenges that a student has attempted at least once with a score > 0.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueSeriousChallengesAttempted
            },
            'studentGoal': False,
        },
        uniqueWarmupChallengesAttempted:{
            'index': uniqueWarmupChallengesAttempted,
            'name':'uniqueWarmupChallengesAttempted',
            'displayName':'# of Unique Warmup Challenges Completed',
            'description':'The number of warmup challenges that a student has attempted at least once.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesAttempted
            },
            'studentGoal': True,
        },   
        uniqueWarmupChallengesGreaterThan60Percent:{
            'index': uniqueWarmupChallengesGreaterThan60Percent,
            'name':'uniqueWarmupChallengesGreaterThan60Percent',
            'displayName':'# of Warmup Challenges Score (>= 60% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal 60%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan60Percent
            },
            'studentGoal': True,
        },
        uniqueWarmupChallengesGreaterThan75Percent:{
            'index': uniqueWarmupChallengesGreaterThan75Percent,
            'name':'uniqueWarmupChallengesGreaterThan75Percent',
            'displayName':'# of Warmup Challenges Score (>= 75% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal 75%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan75Percent
            },
            'studentGoal': True,
        },
        uniqueWarmupChallengesGreaterThan80Percent:{
            'index': uniqueWarmupChallengesGreaterThan80Percent,
            'name':'uniqueWarmupChallengesGreaterThan80Percent',
            'displayName':'# of Warmup Challenges Score (>= 80% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal to 80%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan80Percent
            },
            'studentGoal': True,
        },
        uniqueWarmupChallengesGreaterThan90Percent:{
            'index': uniqueWarmupChallengesGreaterThan90Percent,
            'name':'uniqueWarmupChallengesGreaterThan90Percent',
            'displayName':'# of Warmup Challenges Score (>= 90% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal 90%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan90Percent
            },
            'studentGoal': True,
        },
        uniqueSeriousChallengesGreaterThan30Percent:{
            'index': uniqueSeriousChallengesGreaterThan30Percent,
            'name':'uniqueSeriousChallengesGreaterThan30Percent',
            'displayName':'# of Serious Challenges Score (>= 30% correct)',
            'description':'The number of serious challenges a student has completed with a score equal or greater than 30%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesGreaterThan30Percent
            },
            'studentGoal': True,
        },
        uniqueSeriousChallengesGreaterThan75Percent:{
            'index': uniqueSeriousChallengesGreaterThan75Percent,
            'name':'uniqueSeriousChallengesGreaterThan75Percent',
            'displayName':'# of Serious Challenges Score (>= 75% correct)',
            'description':'The number of serious challenges a student has completed with a score equal or greater than 75%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesGreaterThan75Percent
            },
            'studentGoal': True,
        },
        uniqueSeriousChallengesGreaterThan90Percent:{
            'index': uniqueSeriousChallengesGreaterThan90Percent,
            'name':'uniqueSeriousChallengesGreaterThan90Percent',
            'displayName':'# of Serious Challenges Score (>= 90% correct)',
            'description':'The number of serious challenges a student has completed with a score equal or greater than 90%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueSeriousChallengesGreaterThan90Percent
            },
            'studentGoal': True,
        },
        uniqueWarmupChallengesGreaterThan75PercentForTopic:{
            'index': uniqueWarmupChallengesGreaterThan75PercentForTopic,
            'name':'uniqueWarmupChallengesGreaterThan75PercentForTopic',
            'displayName':'# of Warmup Challenges Score for Specific Topic (>= 75% correct)',
            'description':'The number of warmup challenges a student has completed with a score equal or greater than 75% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueWarmupChallengesGreater75PercentPerTopic
            },
            'studentGoal': False,
        },  
        uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt:{
            'index': uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt,
            'name':'uniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt',
            'displayName':'# of One-attempt Warmup Challenges Score (>= 75% correct)',
            'description':'The number of warmup challenges a student has completed with a score equal or greater than 75% and with only one attempt',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfUniqueWarmupChallengesGreaterThan75WithOnlyOneAttempt
            },
            'studentGoal': True,
        },  
        uniqueWarmupChallengesGreaterThan70PercentTopic:{
            'index': uniqueWarmupChallengesGreaterThan70PercentTopic,
            'name':'uniqueWarmupChallengesGreaterThan70PercentTopic',
            'displayName':'# of Warmup Challenges Score for Specific Topic (>= 70% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal to 70% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueWarmupChallengesGreater70PercentPerTopic
            },
            'studentGoal': False,
        },
        percentageWarmupChallengesGreaterThan75PercentTopic:{
            'index': percentageWarmupChallengesGreaterThan75PercentTopic,
            'name':'percentageWarmupChallengesGreaterThan75PercentTopic',
            'displayName':'Percentage of Warmup Challenges for Specific Topic with >= 75% Correct',
            'description':'The percentage of warmup challenges a student has completed with a score equal or greater than 75% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getPercentageOfUniqueWarmupChallengesGreater75PercentPerTopic
            },
            'studentGoal': False,
        }, 
        uniqueWarmupChallengesGreaterThan85PercentTopic:{
            'index': uniqueWarmupChallengesGreaterThan85PercentTopic,
            'name':'uniqueWarmupChallengesGreaterThan85PercentTopic',
            'displayName':'# of Warmup Challenges Score for Specific Topic (>= 85% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal to 85% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueWarmupChallengesGreater85PercentPerTopic
            },
            'studentGoal': False,
        },
         uniqueWarmupChallengesGreaterThan90PercentTopic:{
            'index': uniqueWarmupChallengesGreaterThan90PercentTopic,
            'name':'uniqueWarmupChallengesGreaterThan90PercentTopic',
            'displayName':'# of Warmup Challenges Score for Specific Topic (>= 90% correct)',
            'description':'The number of warmup challenges a student has completed with a score greater than or equal to 90% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfUniqueWarmupChallengesGreater90PercentPerTopic
            },
            'studentGoal': False,
        },
        percentageWarmupChallengesGreaterThan70PercentTopic:{
            'index': percentageWarmupChallengesGreaterThan70PercentTopic,
            'name':'percentageWarmupChallengesGreaterThan70PercentTopic',
            'displayName':'Percentage of Warmup Challenges for a Specific Topic with >= 70% Correct',
            'description':'The percentage of warmup challenges a student has completed with a score greater than or equal to 70% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getPercentageOfUniqueWarmupChallengesGreater70PercentPerTopic
            },
            'studentGoal': False,
        },  
        percentageWarmupChallengesGreaterThan85PercentTopic:{
            'index': percentageWarmupChallengesGreaterThan85PercentTopic,
            'name':'percentageWarmupChallengesGreaterThan85PercentTopic',
            'displayName':'Percentage of Warmup Challenges for a Specific Topic with >= 85% Correct',
            'description':'The percentage of warmup challenges a student has completed with a score greater than or equal to 85% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getPercentageOfUniqueWarmupChallengesGreater85PercentPerTopic
            },
            'studentGoal': False,
        },
        percentageWarmupChallengesGreaterThan90PercentTopic:{
            'index': percentageWarmupChallengesGreaterThan90PercentTopic,
            'name':'percentageWarmupChallengesGreaterThan90PercentTopic',
            'displayName':'Percentage of Warmup Challenges for a Specific Topic with >= 90% correct',
            'description':'The percentage of warmup challenges a student has completed with a score greater than or equal to 90% for a specific topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getPercentageOfUniqueWarmupChallengesGreater90PercentPerTopic
            },
            'studentGoal': False,
        },  

        warmupChallengesTopicGreaterThan70Percent:{
            'index': warmupChallengesTopicGreaterThan70Percent,
            'name':'warmupChallengesTopicGreaterThan70Percent',
            'displayName':'All Warmup Challenges for Specific Topic are >= 70%',
            'description':'Returns true if all the warmup challenges related to given topic are of greater than or equal to 70%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'boolean',
            'functions':{
                ObjectTypes.topic:allWarmupChallengesTopicGreaterThan70Percent
            },
            'studentGoal': False,
        },  
        warmupChallengesTopicGreaterThan85Percent:{
            'index': warmupChallengesTopicGreaterThan85Percent,
            'name':'warmupChallengesTopicGreaterThan85Percent',
            'displayName':'All Warmup Challenges for Specific Topic are >= 85%',
            'description':'Return True if all the warmup challenges related to given topic are of greater than or equal to 85%. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'boolean',
            'functions':{
                ObjectTypes.topic:allWarmupChallengesTopicGreaterThan85Percent
            },
            'studentGoal': False,
        },  
        averagePercentageOfWarmupsForTopic:{
            'index': averagePercentageOfWarmupsForTopic,
            'name':'averagePercentageOfWarmupsForTopic',
            'displayName':'Average percentage of all the taken warmup challenges related to given topic',
            'description':'Return the average percentage of all the taken warmup challenges related to given topic. The student score only includes the student score, adjustment, and curve.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getAveragePercentageOfWarmupsForTopic
            },
            'studentGoal': False,
        },  
        totalEarndVC:{
            'index': totalEarndVC,
            'name':'totalEarndVC',
            'displayName':'Total Amount of VC Earned',
            'description':'Return the total amount of virtual currency earned by a student',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.virtualCurrencyEarned],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getEarnedVCTotal
            },
            'studentGoal': True,
        },  
        totalSpentVC:{
            'index': totalSpentVC,
            'name':'totalSpentVC',
            'displayName':'Total Amount of VC Spent',
            'description':'Return the total amount of virtual currency spent by a student',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.spendingVirtualCurrency],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getSpentVCTotal
            },
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': False,
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
            'studentGoal': True,
        },      
        duelsSentPerTopic:{
            'index': duelsSentPerTopic,
            'name':'duelsSentPerTopic',
            'displayName':'# of Duels Sent per Topic',
            'description':'The total number of duels a student has sent to other students in a given topic',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.duelSent],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfDuelsSent
            },
            'studentGoal': False,
        },  
        duelsAcceptedPerTopic:{
            'index': duelsAcceptedPerTopic,
            'name':'duelsAcceptedPerTopic',
            'displayName':'# of Duels Accepted Per Topic',
            'description':'The total number of duels a student has accepted from other students in a given topic',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.duelAccepted],  
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfDuelsAccepted
            },
            'studentGoal': False,
        },     
        duelsWonPerTopic:{
            'index': duelsWonPerTopic,
            'name':'duelsWonPerTopic',
            'displayName':'# of Duels Won per Topic',
            'description':'The total number of duels a student has won in a given topic',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.duelWon],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfDuelsWon
            },
            'studentGoal': True,
        },       
        duelsParticipated:{
            'index': duelsParticipated,
            'name':'duelsParticipated',
            'displayName':'# of Duels Participation',
            'description':'The total number of duels a student has participated in a given topic regardless of the duels outcomes',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.duelWon, Event.duelLost],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfDuelsParticipated
            },
            'studentGoal': True,
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
            'studentGoal': False,
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
            'studentGoal': False,
        },  
        calloutParticipate:{
            'index': calloutParticipate,
            'name':'calloutParticipate',
            'displayName':'# of Call Outs Participated in',
            'description':'The total number of call outs a student has participated in weather they won or not',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.calloutWon, Event.calloutLost],  
            },
            'type':'int',
            'functions':{
                ObjectTypes.none:getNumberOfCalloutParticipate
            },
            'studentGoal': True,
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
            'studentGoal': True,
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
            'studentGoal': False,
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
            'studentGoal': False,
        },  
        calloutSentPerTopic:{
            'index': calloutSentPerTopic,
            'name':'calloutSentPerTopic',
            'displayName':'# of Call Outs Sent per topic',
            'description':'The total number of call outs a student has sent to other students',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.calloutSent],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfCalloutSent
            },
            'studentGoal': False,
        },  
        calloutParticipatePerTopic:{
            'index': calloutParticipatePerTopic,
            'name':'calloutParticipatePerTopic',
            'displayName':'# of Call Outs Participated in per topic',
            'description':'The total number of call outs a student has participated in weather they won or not',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.calloutWon, Event.calloutLost],  
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfCalloutParticipate
            },
            'studentGoal': True,
        },     
        calloutParticipationWonPerTopic:{
            'index': calloutParticipationWonPerTopic,
            'name':'calloutParticipationWonPerTopic',
            'displayName':'# of Call Outs a participant has won per topic',
            'description':'The total number of calls out a student has won',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.calloutWon],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfCalloutParticipationWon
            },
            'studentGoal': True,
        },    
        calloutParticipationLostPerTopic:{
            'index': calloutParticipationLostPerTopic,
            'name':'calloutParticipationLostPerTopic',
            'displayName':'# of Call Outs a participant has lost per topic',
            'description':'The total number of call outs a student has lost',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.calloutLost],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfCalloutParticipationLost
            },
            'studentGoal': False,
        },   
        calloutRequestedPerTopic:{
            'index': calloutRequestedPerTopic,
            'name':'calloutRequestedPerTopic',
            'displayName':'# of Call Outs a participant has been reqeusted per topic',
            'description':'The total number of call outs a student has been requested',
            'eventsWhichCanChangeThis':{
                ObjectTypes.topic:[Event.calloutRequested],
            },
            'type':'int',
            'functions':{
                ObjectTypes.topic:getNumberOfCalloutRequested
            },
            'studentGoal': False,
        },  
        studentXP: {
            'index': studentXP,
            'name':'studentXP',
            'displayName':'Student XP',
            'description':'The amount of XP a student currently has',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.activitySubmission, Event.endChallenge, Event.adjustment],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: getStudentXP
            },
            'studentGoal': True,
        },
        studentVC: {
            'index': studentVC,
            'name':'studentVC',
            'displayName':'Student VC',
            'description':'The amount of VC a student currently has',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.virtualCurrencyEarned],
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: getStudentVC
            },
            'studentGoal': True,
        },
        timeSpentOnFlashcards: {
            'index': timeSpentOnFlashcards,
            'name': 'timeSpentOnFlashcards',
            'displayName':'Total Minutes Spent on Flashcards',
            'description':'The sum total time that a student has spent on flashcards.',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.submitFlashCard]
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: getTotalMinutesSpentOnFlashcards
            },
            'studentGoal': True,
        },
        totalFlashcardsCompleted: {
            'index': totalFlashcardsCompleted,
            'name': 'totalFlashcardsCompleted',
            'displayName':'Total Number of Flashcards Completed',
            'description':'The sum total of completed flashcards',
            'eventsWhichCanChangeThis':{
                ObjectTypes.none:[Event.submitFlashCard]
            },
            'type':'int',
            'functions':{
                ObjectTypes.none: getTotalOfCompletedFlashcards
            },
            'studentGoal': True,
        }
                                                                            
    }

if __debug__:
    # Check for mistakes in the systemVariables enum, such as duplicate
    # id numbers or mismatches between eventsWhichCanChangeThis and functions
    expectedFieldsInSysVarStruct = ['index','name','displayName','description','eventsWhichCanChangeThis','type','functions', 'studentGoal']
    
    sysVarNames = [sv for sv in SystemVariable.__dict__ if sv[:1] != '_' and sv != 'systemVariables']
    sysVarNumSet = set()
    for sysVarName in sysVarNames:
        sysVarNum = SystemVariable.__dict__[sysVarName]
        sysVarNumSet.add(sysVarNum)
        assert sysVarNum in SystemVariable.systemVariables, "System variable number created without corresponding structure in systemVariables dictionary.  %s = %i " % (sysVarName,sysVarNum)
        dictEntry = SystemVariable.systemVariables[sysVarNum]
        assert dictEntry["name"] == sysVarName, "Variable %s has incorrect name, %s instead" % (sysVarName,dictEntry["name"])
        assert dictEntry["index"] == sysVarNum, "Variable %s has incorrect index.  Currently %i.  Should be %i instead." % (sysVarName,dictEntry["index"],sysVarNum)
        for field in expectedFieldsInSysVarStruct:
            assert field in dictEntry, "System variable structure missing expected field.  %s missing %s" % (sysVarName,field)
        eventsList = list(dictEntry['eventsWhichCanChangeThis'])
        functionsList = list(dictEntry['functions'])
        assert len([obj for obj in eventsList if obj not in functionsList]) == 0, "System variable structure has an event entry for an object type for which it has no function. %s " % sysVarName
        assert len([obj for obj in functionsList if obj not in eventsList]) == 0, "System variable structure has a functions entry for an object type for which it has no events entry. %s " % sysVarName
        if ObjectTypes.none in eventsList:
            assert len(eventsList) == 1, "System Variable structure has an object which attempts to be in both the global scope (ObjectTypes.none) and one or more specific object scope.  This is not allowed. %s " % sysVarName 
        assert type(dictEntry['studentGoal']) == bool, "System variable field studentGoal is not of type boolean. %s" % (sysVarName)

    assert len(sysVarNames) == len(sysVarNumSet), "Two system variables have the same number."
