import json
import logging

from django.conf import settings
from django.db import OperationalError, transaction
from django.utils.timezone import get_current_timezone_name
from notify.signals import notify

from Badges.enums import (Action, AwardFrequency, Event, ObjectTypes,
                          OperandTypes)
from Badges.models import (ActionArguments, Activities, ActivityCategorySet,
                           ActivitySet, Badges, BadgesInfo, BadgesVCLog,
                           ChallengeSet, Conditions, ConditionSet, Dates,
                           FloatConstants, ProgressiveUnlocking, RuleEvents,
                           Rules, StringConstants, TopicSet,
                           VirtualCurrencyRuleInfo)
from Badges.systemVariables import (calculate_system_variable,
                                    objectTypeToObjectClass)
from Badges.tasks import process_event_offline
from Instructors.constants import unassigned_problems_challenge_name
from Instructors.models import (ActivitiesCategory, Challenges,
                                ChallengesTopics, CoursesTopics,
                                InstructorRegisteredCourses, Topics)
from Instructors.views.utils import current_localtime
from Instructors.views.whoAddedVCAndBadgeView import create_badge_vc_log_json
from Students.models import (Courses, Student, StudentBadges, StudentEventLog,
                             StudentGoalSetting, StudentProgressiveUnlocking,
                             StudentRegisteredCourses, StudentVirtualCurrency,
                             StudentVirtualCurrencyRuleBased, StudentVirtualCurrencyTransactions)
from Students.views.goalView import mark_goal_complete

postgres_enabled = False
if len([db for (name,db) in settings.DATABASES.items() if "postgres" in db['ENGINE']]) > 0:
    postgres_enabled = True
transaction_retry_count = 50
if postgres_enabled:
    from psycopg2.extensions import TransactionRollbackError
else:
    TransactionRollbackError = "Dummy Value which won't match things later"

logger = logging.getLogger(__name__)

# Method to register events with the database and also to
# trigger appropriate action.
# Event should be an integer representing an event from the Event enum.
# Request should be the current active http request object
# If the event involves the student who is currently active as the
# user in the http session, studentID may be omitted.
# If not, such as when an instructor is the active user, it should
# be included.
def register_event_simple(eventID, mini_req, student=None, objectId=None):

    if student is None:
        studentpk = None
    else:
        studentpk = student.pk

    # TODO: As of now, not all places pass in a timezone option
    if not 'timezone' in mini_req:
        mini_req['timezone'] = settings.TIME_ZONE

    # Create event entry and fill in details.
    eventEntry = StudentEventLog()
    eventEntry.event = eventID
    eventEntry.timestamp = current_localtime(tz=mini_req['timezone'])
    courseIDint = int(mini_req['currentCourseID'])
    courseId = Courses.objects.get(pk=courseIDint)
    eventEntry.course = courseId
    if studentpk is None:
        student = Student.objects.get(user__username=mini_req['user'])
    else:
        student = Student.objects.get(pk=studentpk)
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
    if(eventID == Event.adjustment):
        eventEntry.objectType = ObjectTypes.challenge
        eventEntry.objectID = objectId
    if(eventID == Event.challengeExpiration):
        eventEntry.objectType = ObjectTypes.challenge
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
        
    if(eventID == Event.leaderboardUpdate):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId

    if(eventID == Event.classAttendance):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
    if(eventID == Event.spendingVirtualCurrency):
        eventEntry.objectType = ObjectTypes.virtualCurrencySpendRule
        eventEntry.objectID = objectId
        
    # Visited Pages Events    
    if(eventID == Event.visitedDashboard):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
    if(eventID == Event.visitedEarnedVCpage):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
    if(eventID == Event.visitedSpendedVCpage):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
    if(eventID == Event.visitedBadgesInfoPage):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
    if(eventID == Event.visitedVCRulesInfoPage):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0  
    if(eventID == Event.visitedLeaderboardPage):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
    if(eventID == Event.clickedViewAverageGrade):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = 0
                
    # Virtual Currency Events
    if(eventID == Event.instructorHelp):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.buyAttempt):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.extendDeadlineHW):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.extendDeadlineLab):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.replaceLowestAssignGrade):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.buyTestTime):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.getDifferentProblem):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.buyExtraCreditPoints):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.getCreditForOneTestProblem):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.getSurpriseAward):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.buyMissedLab):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.changeHWWeights):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.examExemption):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.activitySubmission):
        eventEntry.objectType = ObjectTypes.form
        eventEntry.objectID = objectId
    if(eventID == Event.virtualCurrencyEarned):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId

    # Duels Events
    if(eventID == Event.duelAccepted):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
    if(eventID == Event.duelLost):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
    if(eventID == Event.duelSent):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
    if(eventID == Event.duelWon):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId

    # Callouts Events
    if(eventID == Event.calloutRequested):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
    if(eventID == Event.calloutLost):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
    if(eventID == Event.calloutSent):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
    if(eventID == Event.calloutWon):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId

    # Badge Events
    if(eventID == Event.badgeEarned):
        eventEntry.objectType = ObjectTypes.none
        eventEntry.objectID = objectId
        
#     if(eventID == Event.seeClassAverage):
#         eventEntry.objectType = ObjectTypes.form
#         eventEntry.objectID = objectId
#     if(eventID == Event.chooseLabPartner):
#         eventEntry.objectType = ObjectTypes.form
#         eventEntry.objectID = objectId
#     if(eventID == Event.chooseProjectPartner):
#         eventEntry.objectType = ObjectTypes.form
#         eventEntry.objectID = objectId
#     if(eventID == Event.uploadOwnAvatar):
#         eventEntry.objectType = ObjectTypes.form
#         eventEntry.objectID = objectId
#     if(eventID == Event.chooseDashboardBackground):
#         eventEntry.objectType = ObjectTypes.form
#         eventEntry.objectID = objectId
#     if(eventID == Event.chooseBackgroundForYourName):
#         eventEntry.objectType = ObjectTypes.form
#         eventEntry.objectID = objectId  
    
    print('eventEntry: '+str(eventEntry))  
    eventEntry.save()

    if settings.CELERY_ENABLED:
        process_event_offline.delay(eventEntry.pk, mini_req, studentpk, objectId)
    else:
        process_event_actual(eventEntry.pk, mini_req, studentpk, objectId)

    return eventEntry

def register_event(eventID, request, student=None, objectId=None):

    def make_smaller_serializable_request(request):
        # This should contain only the parts of request which actually get used by the register_event_actual method
        minireq = {
            'currentCourseID':request.session['currentCourseID'],
            'user':request.user.username,
            'timezone': get_current_timezone_name()
        }
        return minireq

    return register_event_simple(eventID, make_smaller_serializable_request(request), student, objectId)

def process_event_actual(eventID, minireq, studentpk, objectId):
    print("Processing event with eventpk="+str(eventID))
    if studentpk is None:
        student = Student.objects.get(user__username=minireq['user'])
    else:
        student = Student.objects.get(pk=studentpk)

    courseIDint = int(minireq['currentCourseID'])
    courseId = Courses.objects.get(pk=courseIDint)
    
    eventEntry = StudentEventLog.objects.get(pk=eventID)
    
    timestampstr = str(eventEntry.timestamp)
    print("Processing Event with timestamp: "+timestampstr)
    print("Event being processed: "+str(eventEntry))
    
    timezone = minireq['timezone']

    # check for rules which are triggered by this event
    matchingRuleEvents = RuleEvents.objects.filter(rule__courseID=courseId).filter(event=eventEntry.event)
    matchingRuleWithContext = dict()
    logger.debug("Event with timestamp: "+timestampstr+" has "+str(len(matchingRuleEvents))+" matching RuleEvent entries.")
    
    for ruleEvent in matchingRuleEvents:
        print("Event with timestamp: "+timestampstr+" matches with rule "+str(ruleEvent.rule.ruleID))
        if ruleEvent.rule in matchingRuleWithContext:
            matchingRuleWithContext[ruleEvent.rule] = matchingRuleWithContext[ruleEvent.rule] or ruleEvent.inGlobalContext
        else:
            matchingRuleWithContext[ruleEvent.rule] = ruleEvent.inGlobalContext


    for potential in matchingRuleWithContext:
        try:
            condition = potential.conditionID
            
            # First we check if there is an associated award frequency.  If there isn't, we can just check the 
            # rule as is.  That's the simple case because there's no local context.
            if potential.awardFrequency == AwardFrequency.justOnce:
                if check_condition(condition, courseId, student, eventEntry.objectType, eventEntry.objectID, timestampstr):
                    fire_action(potential,courseId,student,eventEntry.objectID, timestampstr, timezone)
            else:            
                objType = AwardFrequency.awardFrequency[potential.awardFrequency]['objectType']
                objSpecifier = ChosenObjectSpecifier(objType,potential.objectSpecifier)
                
                if matchingRuleWithContext[potential]:
                    # The match is for a variable in a global context (either a global variable or a variable inside a for clause
                    objIDList = objSpecifier.getMatchingObjectIds(courseId)
                    objType = objSpecifier.objectType
                    result = True
                else:
                    # The match is for a variable in a local context (a variable from the context of a specifier)
                    result, objType, objIDList = objSpecifier.checkAgainst(eventEntry.objectType,eventEntry.objectID)
    
                if result:
                    for objID in objIDList:
                        if check_condition(condition,courseId,student,objType,objID,timestampstr):
                            fire_action(potential,courseId,student,objID, timestampstr, timezone)
        except Exception as e:
            print('Problem evaluating Rule: '+str(potential)+'  '+str(e))
            pass
            
    return eventEntry

# This method checks whether or not a given condition is true
# in the appropriate context.
def check_condition(condition, course, student, objectType, objectID, timestampstr):
    return check_condition_helper(condition, course, student, 
                                  objectType,objectID, {}, timestampstr)

def operandSetTypeToObjectType(operandType):
    operandSetTypeToOjectTypeMap = {
        OperandTypes.challengeSet: ObjectTypes.challenge,
        OperandTypes.activitySet: ObjectTypes.activity,
        OperandTypes.topicSet: ObjectTypes.topic,
        OperandTypes.activtiyCategorySet:ObjectTypes.activityCategory,
    }
    if operandType in operandSetTypeToOjectTypeMap:
        return operandSetTypeToOjectTypeMap[operandType]
    return 0 # Error

# Helper function for the above.  Includes a hash table so that
# it can avoid loops. (Circular Conditions)
def check_condition_helper(condition, course, student, objectType, objectID, ht, timestampstr):
    if condition in ht:
        return False
    
    print("In Event w/timestamp: "+timestampstr+" Evaluating condition:"+str(condition))
    
    # Fetch operands
    operand1 = get_operand_value(condition.operand1Type,condition.operand1Value, course, student, objectType, objectID, ht, condition, timestampstr)
    
    print("In Event w/timestamp: "+timestampstr+" Operand 1 = "+str(operand1))

    # NOT is our only unary operation.  If we have one, there's no
    # need to do anything with a second operand.
    if (condition.operation == 'NOT'):
        return not operand1
    
    def forallforany_helper(forall):
        for obj in operand1:
            if get_operand_value(condition.operand2Type, condition.operand2Value, course, student, operandSetTypeToObjectType(condition.operand1Type), obj, ht, condition, timestampstr):
                if not forall:
                    return True
            else:
                if forall:
                    return False
        return forall
    if (condition.operation == 'FOR_ALL'):
        return forallforany_helper(True)
    if (condition.operation == 'FOR_ANY'):
        # Here is where we special-case things.  If we're in a virtual currency rule, we treat "for any" as just referring to this particular object.
        # If this particular object is not on the list, we just return false.
#         print("Checking VC workaround in Events!! vcAwardType: "+str(vcAwardType)+"  operandType: "+str(condition.operand1Type))
#         if vcAwardType == AwardFrequency.justOnce or AwardFrequency.awardFrequency[vcAwardType]['objectType']!=operandSetTypeToObjectType(condition.operand1Type):
#             print("Workaround INACTIVE")
        return forallforany_helper(False)
#         else:
#             print("Workaround ACTIVE")
#             if int(objectID) not in operand1:
#                 print("Object: "+str(objectID)+" not in set "+str(operand1))
#                 print(str(type(objectID))+" "+str(type(operand1)))
#                 return False
#             else:
#                 print("Object in set")
#                 return get_operand_value(condition.operand2Type, condition.operand2Value, course, student, objectType, objectID, ht, condition,vcAwardType)
    
    def andor_helper(isAnd):
        for cond in operand1:
            if check_condition_helper(cond, course, student, objectType, objectID, ht, timestampstr):
                if not isAnd:
                    return True
            else:
                if isAnd:
                    return False
        return isAnd
    
    if (condition.operation == 'AND') and (condition.operand1Type == OperandTypes.conditionSet):
        return andor_helper(True)
    if (condition.operation == 'OR') and (condition.operand1Type == OperandTypes.conditionSet):
        return andor_helper(True)

    operand2 = get_operand_value(condition.operand2Type,condition.operand2Value, course, student, objectType, objectID, ht, condition, timestampstr)
    print("In Event w/timestamp: "+timestampstr+" Operand 2 = "+str(operand2))
    
    if (condition.operation == '='):
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
def get_operand_value(operandType,operandValue,course,student,objectType,objectID,ht, condition, timestampstr):
    if (operandType == OperandTypes.immediateInteger):
        return operandValue
    elif (operandType == OperandTypes.boolean):
        return operandValue == 1
    elif (operandType == OperandTypes.condition):
        inner_condition = Conditions.objects.get(pk=operandValue)
        return check_condition_helper(inner_condition, course, student, objectType, objectID,ht, timestampstr)
    elif (operandType == OperandTypes.floatConstant):
        return FloatConstants.objects.get(pk=operandValue).floatValue
    elif (operandType == OperandTypes.stringConstant):
        return StringConstants.objects.get(pk=operandValue).stringValue
    elif (operandType == OperandTypes.dateConstant):
        return Dates.objects.get(pk=operandValue).dateValue
    elif (operandType == OperandTypes.systemVariable):
        return calculate_system_variable(operandValue,course,student,objectType,objectID)
    elif (operandType == OperandTypes.challengeSet):
        if operandValue == 0:
            # All challenges in this course
            return [ch.challengeID for ch in Challenges.objects.filter(courseID = course).exclude(challengeName=unassigned_problems_challenge_name)]
        else:
            return [challset.challenge.challengeID for challset in ChallengeSet.objects.filter(condition=condition)]
    elif (operandType == OperandTypes.activitySet):
        if operandValue == 0:
            # All activities in this course
            return [act.activityID for act in Activities.objects.filter(courseID = course)]
        else:
            return [actset.activity.activityID for actset in ActivitySet.objects.filter(condition=condition)]
    elif (operandType == OperandTypes.topicSet):
        if operandValue == 0:
            # All topics in thie course
            return [ct.topicID.topicID for ct in CoursesTopics.objects.filter(courseID = course)]
        else:
            return [topicset.topic.topicID for topicset in TopicSet.objects.filter(condition=condition)]
    elif (operandType == OperandTypes.activtiyCategorySet):
        if operandValue == 0:
            # All activetyCategory in this course
            return [actCat.categoryID for actCat in ActivitiesCategory.objects.filter(courseID = course)]
        else:
            return [actCatSet.category.categoryID for actCatSet in ActivityCategorySet.objects.filter(condition=condition)]
    elif (operandType == OperandTypes.conditionSet):
        return [condset.conditionInSet for condset in ConditionSet.objects.filter(parentCondition=condition)]
    else:
        return "Bad operand type value"

def fire_action(rule, courseID, studentID, objID, timestampstr, timezone):
    print("In Event w/timestamp: "+timestampstr+" In fire_action for rule "+str(rule))
    actionID = rule.actionID
    args = ActionArguments.objects.filter(ruleID = rule)

    current_time = current_localtime(tz=timezone)

    if (actionID == Action.giveBadge):
        #Give a student a badge.
        badgeIdArg = args.get(sequenceNumber=1)
        badgeIdString = badgeIdArg.argumentValue
        badgeId = int(badgeIdString)
        ##badge = Badges.objects.get(pk=badgeId)
        print("In Event w/timestamp: "+timestampstr+" This is the badge we pick ", badgeId)
        badge = BadgesInfo.objects.get(pk=badgeId)
        
        #Make sure the student hasn't already been awarded this badge
        #If the student has already received this badge, they will not be awarded again
        for retries in range(0,transaction_retry_count):
            try:
                with transaction.atomic():
                    studentBadges = StudentBadges.objects.select_for_update().filter(studentID = studentID, badgeID = badgeId)
                    if rule.awardFrequency != AwardFrequency.justOnce:
                        studentBadges = studentBadges.select_for_update().filter(objectID = objID)
                    for existingBadge in studentBadges:
                        badgeInfo = Badges.objects.select_for_update().get(badgeID = existingBadge.badgeID.badgeID)
                        if(not badgeInfo.manual):
                            autoBadge = Badges.objects.select_for_update().get(badgeID = badgeInfo.badgeID)
                            if autoBadge.ruleID.ruleID == rule.ruleID and autoBadge.courseID.courseID == courseID.courseID:
                            #if existingBadge.badgeID.ruleID.ruleID == rule.ruleID and existingBadge.badgeID.courseID.courseID == courseID.courseID:
                                print("In Event w/timestamp: "+timestampstr+" Student " + str(studentID) + " has already earned badge " + str(badge))
                                return
                        
                    #If the badge has not already been earned, then award it    
                    studentBadge = StudentBadges()
                    studentBadge.studentID = studentID
                    studentBadge.badgeID = badge
                    studentBadge.objectID = objID
                    studentBadge.timestamp = current_time   #Timestamp for badge assignment date
                    studentBadge.save()

                    # Record this trasaction in the log to show that the system awarded this badge
                    studentAddBadgeLog = BadgesVCLog()
                    studentAddBadgeLog.courseID = courseID
                    log_data = create_badge_vc_log_json("System", studentBadge, "Badge", "Automatic")
                    studentAddBadgeLog.log_data = json.dumps(log_data)
                    studentAddBadgeLog.timestamp = current_time
                    studentAddBadgeLog.save()

                    print("In Event w/timestamp: "+timestampstr+" Student " + str(studentID) + " just earned badge " + str(badge) + " with argument " + str(badgeIdArg))
            except OperationalError as e:
                if e.__cause__.__class__ == TransactionRollbackError:
                    continue
                else:
                    raise
            else:
                break
        
        mini_req = {
            'currentCourseID': courseID.pk,
            'user': studentID.user.username,
            'timezone': timezone
        }
        register_event_simple(Event.badgeEarned, mini_req, studentID, badgeId)
        #Test to make notifications 
        notify.send(None, recipient=studentID.user, actor=studentID.user, verb='You won the '+badge.badgeName+'badge', nf_type='Badge', extra=json.dumps({"course": str(courseID.courseID), "name": str(courseID.courseName), "related_link": '/oneUp/students/StudentCourseHome'}))
        
        return
    
    if(actionID == Action.unlockedProgressive):
        print(args)
        # Allow for the content to be unlocked
        ruleIdArg = args.get(sequenceNumber=1)
        # Get unlocking object for the rule
        unlockingID = int (ruleIdArg.argumentValue)
        pUnlockingRule = ProgressiveUnlocking.objects.get(pk=unlockingID)
        objectID = pUnlockingRule.objectID
        print(objectID)
        objectType = pUnlockingRule.objectType
        print(objectType)
        #student = StudentRegisteredCourses.objects.get(studentID = studentID, courseID = courseID)
        StudnetPUnlockingRule = StudentProgressiveUnlocking.objects.get(studentID = studentID, courseID=courseID, objectID= objectID,objectType = objectType)
        StudnetPUnlockingRule.isFullfilled = True
        StudnetPUnlockingRule.save()
        print("Student " + str(studentID) + " just unlocked " + pUnlockingRule.name + " with argument " + str(ruleIdArg))
        # TODO: The related link here should be updated based on the object type
        notify.send(None, recipient=studentID.user, actor=studentID.user, verb='You have unlocked an '+ ObjectTypes.objectTypes.get(objectType), nf_type='progressiveUnlocking', extra=json.dumps({"course": str(courseID.courseID), "name": str(courseID.courseName), "related_link": '/oneUp/students/ChallengesList'}))        

        return
    
    if (actionID == Action.createNotification):
        print("In Event w/timestamp: "+timestampstr+" In notifications ")

        #Create a notification.
        return
    if actionID == Action.completeGoal:
        goal_name = args.get(sequenceNumber=1).argumentValue
        print(f"About to complete goal {goal_name} for {studentID} in course {courseID.courseName}")
        
        for retries in range(0,transaction_retry_count):
            try:
                with transaction.atomic(): 
                    goal = StudentGoalSetting.objects.select_for_update().get(ruleID=rule)
                    if goal.completed:
                        print(f"[SKIP] The goal, {goal_name}, has already been completed for {studentID} in course {courseID.courseName}")
                        return

                    notify.send(None, recipient=studentID.user, actor=studentID.user, verb=f"{goal_name} personal goal has been completed", nf_type='goal', extra=json.dumps(
                        {"course": str(courseID.courseID), "name": str(courseID.courseName), "related_link": '/oneUp/students/goalslist'}))

                    mark_goal_complete(goal)
                    print(f"The goal, {goal_name}, is completed for {studentID} in course {courseID.courseName}")

            except OperationalError as e:
                if e.__cause__.__class__ == TransactionRollbackError:
                    continue
                else:
                    raise
            else:
                break

       
    if (actionID == Action.addSkillPoints):
        #Add skill points to a student
        return
    
    if actionID == Action.increaseVirtualCurrency or actionID == Action.decreaseVirtualCurrency:
        ruleIdArg = args.get(sequenceNumber=1)
        # Get the virtual currency that is associated with the rule
        ruleIdString = ruleIdArg.argumentValue
        vcRuleAmount = int(ruleIdString)
        # Get the student
        student = StudentRegisteredCourses.objects.get(studentID = studentID, courseID = courseID)

        vcRule = VirtualCurrencyRuleInfo.objects.get(ruleID=rule)
        print("[TEST1] Begin reward student with VC")
        for retries in range(0,transaction_retry_count):
            try:
                with transaction.atomic(): 
                    if actionID == Action.increaseVirtualCurrency:
                        print("[TEST2] Checking if student was already awarded")
                        previousAwards = StudentVirtualCurrencyRuleBased.objects.select_for_update().filter(studentID = student.studentID, vcRuleID = vcRule)
                        if rule.awardFrequency != AwardFrequency.justOnce:
                            previousAwards = previousAwards.filter(objectID = objID)
                        if previousAwards.exists():
                            # Student was already awarded this virtual currency award for this object and this rule.  Do nothing.
                            print("[TEST3] In Event w/timestamp:"+timestampstr+" Student was previously awarded this virtual currency award.")
                            return
                                    
                        studVCRec = StudentVirtualCurrencyRuleBased()
                        studVCRec.courseID = courseID
                        studVCRec.studentID = student.studentID
                        studVCRec.timestamp = current_time
                        if rule.awardFrequency == AwardFrequency.justOnce:
                            studVCRec.objectID = 0
                        else:
                            studVCRec.objectID = objID
                        studVCRec.vcRuleID = vcRule
                        studVCRec.save()

                        # Record this trasaction in the log to show that the system awarded this vc
                        studentAddBadgeLog = BadgesVCLog()
                        studentAddBadgeLog.courseID = courseID
                        log_data = create_badge_vc_log_json("System", studVCRec, "VC", "Automatic")
                        studentAddBadgeLog.log_data = json.dumps(log_data)
                        studentAddBadgeLog.timestamp = current_time
                        studentAddBadgeLog.save()

                        print("[TEST4] StudentVirtualCurrencyRuleBased object was saved.")
            except OperationalError as e:
                if e.__cause__.__class__ == TransactionRollbackError:
                    continue
                else:
                    raise
            else:
                break
        
        if actionID == Action.increaseVirtualCurrency:
            '''print("[TEST5] About to increase student VC amount")
            # Increase the student virtual currency amount
            for retries in range(0,transaction_retry_count):
                try:
                    with transaction.atomic():
                        student = StudentRegisteredCourses.objects.get(studentID = studentID, courseID = courseID)
                        #student = StudentRegisteredCourses.objects.select_for_update().get(studentID = studentID, courseID = courseID)
                        print("[TEST6-preinc] oldVCAmount:"+str(student.virtualCurrencyAmount))
                        student.virtualCurrencyAmount += vcRuleAmount
                        student.save()
                        print("[TEST6-postinc] newVCAmount:"+str(student.virtualCurrencyAmount))
                        transaction.on_commit(lambda:[student.refresh_from_db(),print("[TEST6-postinc] transaction committed.  VCAmount: " +str(student.virtualCurrencyAmount))])

                    print("[TEST6] Student VC amount increased.")

                    mini_req = {
                        'currentCourseID': courseID.pk,
                        'user': studentID.user.username,
                        'timezone': timezone
                    }
                    register_event_simple(Event.virtualCurrencyEarned, mini_req, studentID, vcRuleAmount)
                    print("[TEST7] End. VC earned event registered")
                except OperationalError as e:
                    print("[TEST8] Operational Error! :"+str(e))
                    if e.__cause__.__class__ == TransactionRollbackError:
                        continue
                    else:
                        raise
                else:
                    print("[TEST8] No exception raised!")
                    break'''
            recalculate_student_virtual_currency_total(studentID, courseID)
            notify.send(None, recipient=studentID.user, actor=studentID.user, verb='You won '+str(vcRuleAmount)+' course bucks', nf_type='Increase VirtualCurrency', extra=json.dumps({"course": str(courseID.courseID), "name": str(courseID.courseName), "related_link": '/oneUp/students/Transactions'}))
            return
        
        if actionID == Action.decreaseVirtualCurrency:
            # Decrease the student virtual currency amount
            
            # Commented this out for now since not all shop items are reaching this point (they may not have rules)
            # Each shop item should have a rule associated with it though. This needs to be looked into more

#             for retries in range(0,transaction_retry_count):
#                 try:
#                     with transaction.atomic():
#                         student = StudentRegisteredCourses.objects.get(studentID = studentID, courseID = courseID)
            if student.virtualCurrencyAmount >= vcRuleAmount:
#                             student.virtualCurrencyAmount -= vcRuleAmount 
#                             instructorCourse = InstructorRegisteredCourses.objects.filter(courseID=courseID).first()
#                             instructor = instructorCourse.instructorID
#                             notify.send(None, recipient=instructor, actor=studentID.user, verb= studentID.user.first_name +' '+studentID.user.last_name+ ' spent '+str(vcRuleAmount)+' course bucks', nf_type='Decrease VirtualCurrency')
                logger.warn("This shop item has a rule associated with it, but currency deduction and instructor notification is handled in virtualCurrencyShopView.py instead")
            else:
#                            #Notify that this purchase did not go through                        #### STILL TO BE IMPLEMENTED
                print("In Event w/timestamp: "+timestampstr+' this purchase did not go through')
#                         student.save()
#                 except OperationalError as e:
#                     if e.__cause__.__class__ == TransactionRollbackError:
#                         continue
#                     else:
#                         raise
#                 else:
#                     break
            return

chosenObjectSpecifierFields = {
    ObjectTypes.activity:{
        'id': {
            'fun': lambda act: [act.activityID],
            'selectionType': 'object',
            'objectType': ObjectTypes.activity,
            'addfilter': lambda objs,idlist: objs.filter(pk__in=idlist)
        },
        'category': {
            'fun': lambda act: [act.category.categoryID],
            'selectionType': 'object',
            'objectType': ObjectTypes.activityCategory,
            'addfilter': lambda objs,catlist: objs.filter(category__pk__in=catlist),
        },
    },
    ObjectTypes.challenge:{
        'id': {
            'fun': lambda chall: [chall.challengeID],
            'selectionType': 'object',
            'objectType': ObjectTypes.challenge,
            'addfilter': lambda objs,idlist: objs.filter(pk__in=idlist),
        },
        'topic': {
            'fun': lambda chall: [ct.topicID.topicID for ct in ChallengesTopics.objects.filter(challengeID=chall)],
            'selectionType': 'object',
            'objectType': ObjectTypes.topic,
            'addfilter': lambda objs,topiclist: objs.filter(topicID__pk__in=topiclist),
        },
        'type': {
            'fun': lambda chall: ['serious' if chall.isGraded else 'warmup'],
            'selectionType': 'list',
            'list': ['serious','warmup'],
            'addfilter': lambda objs, valueList: objs.filter(isGraded=(valueList[0]=='serious')),
        },
    },
    ObjectTypes.topic:{
        'id': {
            'fun': lambda topic: [topic.topicID],
            'selectionType': 'object',
            'objectType': ObjectTypes.topic,
            'addfilter': lambda objs,idlist: objs.filter(pk__in=idlist),
        },
    },
    ObjectTypes.activityCategory:{
        'id': {
            'fun': lambda ac: [ac.categoryID],
            'selectionType': 'object',
            'objectType': ObjectTypes.activityCategory,
            'addfilter': lambda objs,idlist: objs.filter(pk__in=idlist),
        },
    },
    ObjectTypes.none:{},
}

objectTypesToObjects = {
    ObjectTypes.challenge: Challenges,
    ObjectTypes.activity: Activities,
    ObjectTypes.topic: Topics,
    ObjectTypes.activityCategory: ActivitiesCategory,
}

objectTypesToGetAllFromCourse = {
    ObjectTypes.challenge: lambda course: Challenges.objects.filter(courseID = course),
    ObjectTypes.activity: lambda course: Activities.objects.filter(courseID = course),
    ObjectTypes.topic: lambda course: CoursesTopics.objects.filter(courseID = course).select_related("topicID"),
    ObjectTypes.activityCategory: lambda course: ActivitiesCategory.objects.filter(courseID = course),
}
    
def objectTypeFromObject(obj):
    if type(obj) is Challenges:
        return ObjectTypes.challenge
    if type(obj) is Activities:
        return ObjectTypes.activity
    if type(obj) is Topics:
        return ObjectTypes.topic
    if type(obj) is ActivitiesCategory:
        return ObjectTypes.activityCategory

relatedObjects = {
    ObjectTypes.activityCategory: {
        ObjectTypes.activity: (lambda act: [act.category.categoryID]),
    },
    ObjectTypes.topic: {
        ObjectTypes.challenge: (lambda chall: [ct.topicID.topicID for ct in ChallengesTopics.objects.filter(challengeID=chall)])
    },
}                 

class ChosenObjectSpecifier:
    # str is expected to be a JSON serialized list of specifier rules.
    # Each specifier rule is a dictionary with the following entries:
    #     'specifier' -- should contain a specifier from the allowed list (the list can be found in the
    #                    chosenObjectSpecifierFields above).  Note that which type of object is in use changes
    #                    which specifiers are allowed.
    #     'op' -- which operation is being used to specify.  Currently only 'in' is allowed in this field
    #     'value' -- a value whose type depends on the specifier and the op.  For 'id' and 'in', it should be
    #                a list of primary key values of the appropriate type
    #                For ('topic' or 'category') and 'in', it should be a list of the primary key values
    #                of those types
    #                For 'type' it should be either ['serious'] or ['warmup']  (both is allowed, but is normally
    #                expressed by omitting a rule altogether since no narrowing is needed).
    def __init__(self,objectType = ObjectTypes.none, serialized_value = "[]"):
        self.rules = json.loads(serialized_value)
        self.objectType = objectType
        valid = True
        print("unserialized self.rules:" +str(self.rules))
        for rule in self.rules:
            if 'specifier' not in rule:
                valid = False
                print("no specifier")
                break
            if rule['specifier'] not in chosenObjectSpecifierFields[objectType]:
                valid = False
                print("bad specifier")
                break
            if 'op' not in rule:
                valid = False
                print("no op")
                break
            if rule['op'] != 'in': # More options will be allowed in the future
                valid = False
                print("bad op")
                break
            if 'value' not in rule:
                valid = False
                print("no value")
                break
            if type(rule['value']) is not list: # Note that we don't validate the contents of the list so things could still go wrong there
                valid = False
                print("value not list instead is "+str(type(rule['value'])))
                break
        
        if not valid:
            self.rules = []
    
    def __str__(self):
        return json.dumps(self.rules)
    
    def checkAgainst(self,objType,objID):    
        if self.objectType == ObjectTypes.none:
            return True, objType, [objID]
        if objType == ObjectTypes.none:
            return True, objType, [objID]
        obj = objectTypeToObjectClass[objType].objects.get(pk=objID)
        if self.objectType == objType:

            for rule in self.rules:
                if rule['op'] == 'in':
                    objThingieList = chosenObjectSpecifierFields[self.objectType][rule['specifier']]['fun'](obj)
                    found = False
                    print("rule[value] = "+str(rule['value']))
                    print("objThingieList:"+str(objThingieList))
                    for objThingie in objThingieList:   # We check all the thingies against the list.  For many cases
                                                        # this is just one thing, actually, like id, but for topic
                                                        # challenges can be in more than one topic.  If any of its
                                                        # topics meet the specifier, that's sufficient.
                        if str(objThingie) in rule['value']:
                            found = True
                            break
                    if found == False: # If any one specifier is not met, we're done, otherwise, we continue
                        return False, objType, []
            return True, objType, [objID]
        if self.objectType in relatedObjects:
            if objType in relatedObjects[self.objectType]:
                relatedObjs = relatedObjects[self.objectType][objType](obj)
                outputList = []
                for relObjID in relatedObjs:
                    if self.checkAgainst(objType,relObjID):
                        outputList.append(relObjID)
                if outputList:
                    return True, self.objectType, outputList
                else:
                    return False, objType, []
                
        # This last case should not actually happen due to how the code which calls this code is structured,
        # but we're going to default to success since that's less likely to cause problems in the event that
        # something went wrong.  It may sometimes cause problems, but that's likely preferable to always
        # giving an error right now.
        return True, objType, [objID]
    
    def getMatchingObjectIds(self,course):
        objects = objectTypesToGetAllFromCourse[self.objectType](course)
        for rule in self.rules:
            if rule['op'] == 'in':
                objects = chosenObjectSpecifierFields[self.objectType][rule['specifier']]['addfilter'](objects,rule['value'])
        return [obj.pk for obj in objects]
    
def recalculate_student_virtual_currency_total(student,course):
    total = 0
    earningTransations = StudentVirtualCurrency.objects.filter(courseID=course, studentID=student)
    for et_svc in earningTransations:
        if hasattr(et_svc, 'studentvirtualcurrencyrulebased'):
            vcrule = et_svc.studentvirtualcurrencyrulebased.vcRuleID
            if not vcrule:
                # This shouldn't occur, but just in case there are broken entries, we'll skip them
                continue
            if vcrule.vcRuleAmount != -1:
                total += et_svc.value
            else:
                avcr = VirtualCurrencyRuleInfo.objects.filter(vcRuleID=vcrule.vcRuleID).first()
                if avcr:
                    if (ActionArguments.objects.filter(ruleID=avcr.ruleID).exists()):
                        total += int(ActionArguments.objects.get(ruleID=avcr.ruleID).argumentValue)
        else:
            total += et_svc.value
      
    spendingTransactions = StudentVirtualCurrencyTransactions.objects.filter(student=student, course=course).filter(studentEvent__event=Event.spendingVirtualCurrency)
    for st_svct in spendingTransactions:
        if st_svct.status in ['In Progress', 'Requested','Complete']:
            total -= st_svct.amount
    
    studentRegCourse = StudentRegisteredCourses.objects.get(courseID=course,studentID = student)
    studentRegCourse.virtualCurrencyAmount = total
    print("[VCRecalculate] Total: "+str(total))
    studentRegCourse.save()
