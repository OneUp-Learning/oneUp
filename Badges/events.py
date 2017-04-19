from Badges.models import Rules, ActionArguments, Conditions, Badges
from Badges.models import FloatConstants, StringConstants
from Badges.enums import OperandTypes, ObjectTypes, Event, SystemVariable, Action
from Students.models import StudentBadges, StudentEventLog, Courses, StudentChallenges, Student,\
    StudentRegisteredCourses
from datetime import datetime
from django.utils import timezone
from builtins import getattr
import decimal
from Instructors.models import Challenges

# Method to register events with the database and also to
# trigger appropriate action.
# Event should be an integer representing an event from the Event enum.
# Request should be the current active http request object
# If the event involves the student who is currently active as the
# user in the http session, studentID may be omitted.
# If not, such as when an instructor is the active user, it should
# be included.
def register_event(eventID, request, student=None, objectId=None):

    print('in register_event: ')
    print(str(eventID))
    # Create event log entry and fill in details.
    eventEntry = StudentEventLog()
    eventEntry.event = eventID
    eventEntry.timestamp = datetime.now()
    courseIDint = int(request.session['currentCourseID'])
    courseId = Courses.objects.get(pk=courseIDint)
    eventEntry.course = courseId
    if (student is None):
        student = Student.objects.get(user=request.user)
    eventEntry.student = student

    # Here we need to add special handling for different types
    # of events which can occur
    if(eventID == Event.startChallenge):
        eventEntry.objectType = ObjectTypes.challenge
        eventEntry.objectID = objectId
    if (eventID == Event.endChallenge):
        eventEntry.objectType = ObjectTypes.challenge
        eventEntry.objectID = objectId
    if(eventID == Event.completeQuestion): 
        eventEntry.objectType = ObjectTypes.question
        eventEntry.objectID = objectId
    if(eventID == Event.participationNoted):
        eventEntry.objectType = ObjectTypes.activity
        eventEntry.objectID = objectId
    if(eventID == Event.timePassed):
        eventEntry.objectType = ObjectTypes.challenge #consider doing something similar for specific questions also
        eventEntry.objectID = objectId
   
    #if(eventID == Event.valueChanged):
        
    if(eventID == Event.startQuestion):
        eventEntry.objectType = ObjectTypes.question
        eventEntry.objectID = objectId
    if (eventID == Event.endQuestion):
        eventEntry.objectType = ObjectTypes.question
        eventEntry.objectID = objectId
    if(eventID == Event.userLogin):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = courseIDint #login form may not have an object id
    if(eventID == Event.challengeExpiration):
        eventEntry.objectType = ObjectTypes.challenge
        eventEntry.objectID = objectId
    
    # Virtual Currency Events
    if(eventID == Event.buyAttempt):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.buyHint):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.extendDeadline):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.dropLowestAssignGrade):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.getDifferentProblem):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.seeClassAverage):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.chooseLabPartner):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.chooseProjectPartner):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.uploadOwnAvatar):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.chooseDashboardBackground):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.getSurpriseAward):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.chooseBackgroundForYourName):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    
    print('eventEntry: '+str(eventEntry))  
    eventEntry.save()
    
    
    # check for rules which are triggered by this event
    potentials = Rules.objects.filter(courseID=courseId).filter(ruleevents__event=eventID)
    print(potentials)
    for potential in potentials:
        condition = potential.conditionID
        if check_condition(condition,courseId,student,eventEntry.objectType,objectId):
            print('after check_condition')
            fire_action(potential,courseId,student,objectId)
            
    return eventEntry

# This method checks whether or not a given condition is true
# in the appropriate context.
def check_condition(condition, course, student, objectType, objectID):
    return check_condition_helper(condition, course, student, 
                                  objectType,objectID, {})

# Helper function for the above.  Includes a hash table so that
# it can avoid loops. (Circular Conditions)
def check_condition_helper(condition, course, student, objectType, objectID, ht):
    if condition in ht:
        return False
    
    print("Evaluating condition:"+str(condition))
    
    # Fetch operands
    operand1 = get_operand_value(condition.operand1Type,condition.operand1Value, course, student, objectType, objectID, ht)
    
    print("Operand 1 = "+str(operand1))

    # NOT is our only unary operation.  If we have one, there's no
    # need to do anything with a second operand.
    if (condition.operation == 'NOT'):
        return not operand1

    operand2 = get_operand_value(condition.operand2Type,condition.operand2Value, course, student, objectType, objectID, ht)
    print("Operand 2 = "+str(operand2))
    
    if (condition.operation == '=='):
        return operand1==operand2
    if (condition.operation == '>'):
        return operand1>operand2
    if (condition.operation == '<'):
        return operand1<operand2
    if (condition.operation == '>='):
        return operand1>=operand2
    if (condition.operation == '<='):
        return operand1<=operand2
    if (condition.operation == '!='):
        return operand1!=operand2
    if (condition.operation == 'AND'):
        return operand1 and operand2
    if (condition.operation == 'OR'):
        return operand1 or operand2

# Takes and operand type and value and finds the appropriate
# value for it.
def get_operand_value(operandType,operandValue,course,student,objectType,objectID,ht):
    if (operandType == OperandTypes.immediateInteger):
        return operandValue
    elif (operandType == OperandTypes.condition):
        condition = Conditions.objects.get(pk=operandValue)
        return check_condition_helper(condition, course, student, objectType, objectID,ht)
    elif (operandType == OperandTypes.floatConstant):
        return FloatConstants.objects.get(pk=operandValue)
    elif (operandType == OperandTypes.stringConstant):
        return StringConstants.objects.get(pk=operandValue)
    elif (operandType == OperandTypes.systemVariable):
        return calculate_system_variable(operandValue,course,student,objectType,objectID)
    else:
        return "Bad operand type value"

# This is where we evaluate the system variables in their appropriate
# context.
def calculate_system_variable(varIndex,course,student,objectType,objectID):
    print("VarIndex: " + str(varIndex))
        
    #Return the number of attempts (looking at only the startChallenge event trigger 801)
    if (varIndex == SystemVariable.numAttempts):
        numberOfAttempts = StudentEventLog.objects.filter(course = course, student = student, objectType = objectType, objectID = objectID, event = Event.endChallenge).count()
        return numberOfAttempts
    
    #Return the test score from the fired event
    #Event enum is unspecified because it could be triggered on multiple occasions
    if (varIndex == SystemVariable.testScore):
        scores = StudentChallenges.objects.filter(challengeID = objectID,courseID = course,studentID = student)
        if len(scores) == 0:
            return 0 
        return scores.latest('testScore').testScore #Ensure that only the most recent test score is returned
    
    #Return the actual correct percentage from the fired event
    if (varIndex == SystemVariable.percentageCorrect):
        #Get the student score
        allScores = StudentChallenges.objects.filter(challengeID = objectID,courseID = course,studentID = student)
        if allScores.exists():
            testScore = allScores.latest('testScore')
        else:
            return 0

        #Check if denominator is zero to avoid getting a DivideByZero error
        if float(testScore.testTotal) != 0:
            percentCorrect = (float(testScore.testScore)/float(testScore.testTotal)) * 100
        return percentCorrect
    
    def getAllTestScores():
        return StudentChallenges.objects.filter(courseID = course, studentChallengeID = objectID)
    
    #return the highest test score achieved out of the entire class for a challenge
    if (varIndex == SystemVariable.maxTestScore):
        allTestScores = getAllTestScores()
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

def fire_action(rule,courseID,studentID,objectIDPassed):
    print("In fire_action ")
    actionID = rule.actionID
    args = ActionArguments.objects.filter(ruleID = rule)
    if (actionID == Action.giveBadge):
        #Give a student a badge.
        badgeIdArg = args.get(sequenceNumber=1)
        badgeIdString = badgeIdArg.argumentValue
        badgeId = int(badgeIdString)
        badge = Badges.objects.get(pk=badgeId)
        
        #Make sure the student hasn't already been awarded this badge
        #If the student has already received this badge, they will not be awarded again
        studentBadges = StudentBadges.objects.filter(studentID = studentID, badgeID = badgeId, objectID = objectIDPassed)
        for existingBadge in studentBadges:
            if existingBadge.badgeID.ruleID.ruleID == rule.ruleID and existingBadge.badgeID.courseID.courseID == courseID.courseID:
                print("Student " + str(studentID) + " has already earned badge " + str(badge))
                return
            
        #If the badge has not already been earned, then award it    
        studentBadge = StudentBadges()
        studentBadge.studentID = studentID
        studentBadge.badgeID = badge
        studentBadge.objectID = objectIDPassed
        studentBadge.timestamp = datetime.now()         # AV #Timestamp for badge assignment date
        studentBadge.save()
        print("Student " + str(studentID) + " just earned badge " + str(badge) + " with argument " + str(badgeIdArg))
        return
    if (actionID == Action.createNotification):
        #Create a notification.
        return
    if (actionID == Action.addSkillPoints):
        #Add skill points to a student
        return
    
    if (actionID == Action.increaseVirtualCurrency):
        ruleIdArg = args.get(sequenceNumber=1)
        # Get the virtual currency that is associated with the rule
        ruleIdString = ruleIdArg.argumentValue
        vcRuleAmount = int(ruleIdString)
        # Get the student
        student = StudentRegisteredCourses.objects.get(studentID = studentID, courseID = courseID)
        # Increase the student virtual currency amount
        student.virtualCurrencyAmount += vcRuleAmount
        student.save()
        return
    
    if (actionID == Action.decreaseVirtualCurrency):
        ruleIdArg = args.get(sequenceNumber=1)
        # Get the virtual currency that is associated with the rule
        ruleIdString = ruleIdArg.argumentValue
        vcRuleAmount = int(ruleIdString)
        # Get the student
        student = StudentRegisteredCourses.objects.get(studentID = studentID, courseID = courseID)
        # Increase the student virtual currency amount
        student.virtualCurrencyAmount -= vcRuleAmount
        student.save()
        return
