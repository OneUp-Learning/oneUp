from Badges.models import Rules, ActionArguments, Conditions, BadgesInfo, Badges,\
    ActivitySet, VirtualCurrencyRuleInfo
from Badges.models import FloatConstants, StringConstants, ChallengeSet, TopicSet, Activities, ConditionSet, Dates, ActivityCategorySet
from Badges.enums import OperandTypes, ObjectTypes, Event, Action,\
    VirtualCurrencyAwardFrequency
from Students.models import StudentBadges, StudentEventLog, Courses, Student,\
    StudentRegisteredCourses, StudentVirtualCurrency
from datetime import datetime
from django.utils import timezone
from builtins import getattr
import decimal
from Instructors.models import Challenges, CoursesTopics, ActivitiesCategory
from Badges.systemVariables import calculate_system_variable
from Instructors.views.utils import utcDate
from Instructors.constants import unassigned_problems_challenge_name
from notify.signals import notify
from django.contrib.auth.models import User
from Instructors.models import InstructorRegisteredCourses, Instructors


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
    eventEntry.timestamp = utcDate()
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
    if(eventID == Event.adjustment):
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
    if(eventID == Event.challengeExpiration):
        eventEntry.objectType = ObjectTypes.challenge
        eventEntry.objectID = objectId
        
    if(eventID == Event.leaderboardUpdate):
        eventEntry.objectType = ObjectTypes.none
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
    
    # check for rules which are triggered by this event
    potentials = Rules.objects.filter(courseID=courseId).filter(ruleevents__event=eventID)
    print(potentials)
    for potential in potentials:
        condition = potential.conditionID

        ## KI: All of this vcAwardType stuff is hacky.  When there's enough time to make sure everything is done right
        ## we should replace it with a more complete interface for having certain conditions specific to 
        ## the object which the event creates.
        vcRule = VirtualCurrencyRuleInfo.objects.filter(ruleID=potential.ruleID).first()
        if vcRule:
            vcAwardType = vcRule.awardFrequency
        else:
            vcAwardType = VirtualCurrencyAwardFrequency.justOnce
        if check_condition(condition,courseId,student,eventEntry.objectType,objectId,vcAwardType):
            print('after check_condition')
            fire_action(potential,courseId,student,eventEntry)
            
    return eventEntry

# This method checks whether or not a given condition is true
# in the appropriate context.
def check_condition(condition, course, student, objectType, objectID, vcAwardType):
    return check_condition_helper(condition, course, student, 
                                  objectType,objectID, {}, vcAwardType)

# Helper function for the above.  Includes a hash table so that
# it can avoid loops. (Circular Conditions)
def check_condition_helper(condition, course, student, objectType, objectID, ht, vcAwardType):
    if condition in ht:
        return False
    
    print("Evaluating condition:"+str(condition))
    
    # Fetch operands
    operand1 = get_operand_value(condition.operand1Type,condition.operand1Value, course, student, objectType, objectID, ht, condition,vcAwardType)
    
    print("Operand 1 = "+str(operand1))

    # NOT is our only unary operation.  If we have one, there's no
    # need to do anything with a second operand.
    if (condition.operation == 'NOT'):
        return not operand1
    
    def operandSetTypeToObjectType(operandType):
        if (operandType == OperandTypes.challengeSet):
            return ObjectTypes.challenge
        if (operandType == OperandTypes.activitySet):
            return ObjectTypes.activity
        if (operandType == OperandTypes.topicSet):
            return ObjectTypes.topic
        if (operandType == OperandTypes.activtiyCategorySet):
            return ObjectTypes.activtyCategory
        return 0 # Error
    def forallforany_helper(forall):
        for object in operand1:
            if get_operand_value(condition.operand2Type, condition.operand2Value, course, student, operandSetTypeToObjectType(condition.operand1Type), object, ht, condition,vcAwardType):
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
        print("Checking VC workaround in Events!! vcAwardType: "+str(vcAwardType)+"  operandType: "+str(condition.operand1Type))
        if vcAwardType == VirtualCurrencyAwardFrequency.justOnce or VirtualCurrencyAwardFrequency.virtualCurrencyAwardFrequency[vcAwardType]['objectType']!=operandSetTypeToObjectType(condition.operand1Type):
            print("Workaround INACTIVE")
            return forallforany_helper(False)
        else:
            print("Workaround ACTIVE")
            if int(objectID) not in operand1:
                print("Object: "+str(objectID)+" not in set "+str(operand1))
                print(str(type(objectID))+" "+str(type(operand1)))
                return False
            else:
                print("Object in set")
                return get_operand_value(condition.operand2Type, condition.operand2Value, course, student, objectType, objectID, ht, condition,vcAwardType)
    
    def andor_helper(isAnd):
        for cond in operand1:
            if check_condition_helper(cond, course, student, objectType, objectID, ht, vcAwardType):
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

    operand2 = get_operand_value(condition.operand2Type,condition.operand2Value, course, student, objectType, objectID, ht, condition, vcAwardType)
    print("Operand 2 = "+str(operand2))
    
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
def get_operand_value(operandType,operandValue,course,student,objectType,objectID,ht, condition, vcAwardType):
    if (operandType == OperandTypes.immediateInteger):
        return operandValue
    elif (operandType == OperandTypes.boolean):
        return operandValue == 1
    elif (operandType == OperandTypes.condition):
        inner_condition = Conditions.objects.get(pk=operandValue)
        return check_condition_helper(inner_condition, course, student, objectType, objectID,ht,vcAwardType)
    elif (operandType == OperandTypes.floatConstant):
        return FloatConstants.objects.get(pk=operandValue)
    elif (operandType == OperandTypes.stringConstant):
        return StringConstants.objects.get(pk=operandValue)
    elif (operandType == OperandTypes.dateConstant):
        return Dates.objects.get(pk=operandValue)
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

def fire_action(rule,courseID,studentID,eventEntry):
    print("In fire_action ")
    actionID = rule.actionID
    args = ActionArguments.objects.filter(ruleID = rule)
    if (actionID == Action.giveBadge):
        #Give a student a badge.
        badgeIdArg = args.get(sequenceNumber=1)
        badgeIdString = badgeIdArg.argumentValue
        badgeId = int(badgeIdString)
        ##badge = Badges.objects.get(pk=badgeId)
        print("This is the badge we pick ", badgeId)
        badge = BadgesInfo.objects.get(pk=badgeId)
        
        #Make sure the student hasn't already been awarded this badge
        #If the student has already received this badge, they will not be awarded again
        studentBadges = StudentBadges.objects.filter(studentID = studentID, badgeID = badgeId)
        for existingBadge in studentBadges:
            badgeInfo = Badges.objects.get(badgeID = existingBadge.badgeID.badgeID)
            if(not badgeInfo.manual):
                autoBadge = Badges.objects.get(badgeID = badgeInfo.badgeID)
                if autoBadge.ruleID.ruleID == rule.ruleID and autoBadge.courseID.courseID == courseID.courseID:
                #if existingBadge.badgeID.ruleID.ruleID == rule.ruleID and existingBadge.badgeID.courseID.courseID == courseID.courseID:
                    print("Student " + str(studentID) + " has already earned badge " + str(badge))
                    return
            
        #If the badge has not already been earned, then award it    
        studentBadge = StudentBadges()
        studentBadge.studentID = studentID
        studentBadge.badgeID = badge
        studentBadge.objectID = eventEntry.objectID
        studentBadge.timestamp = utcDate()         # AV #Timestamp for badge assignment date
        studentBadge.save()
        print("Student " + str(studentID) + " just earned badge " + str(badge) + " with argument " + str(badgeIdArg))
        
        #Test to make notifications 
        notify.send(None, recipient=studentID.user, actor=studentID.user, verb='You Won a '+badge.badgeName+'Badge', nf_type='Badge')
        
        return
    
    if (actionID == Action.createNotification):
        print("In notifications ")

        #Create a notification.
        return
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
        
        if actionID == Action.increaseVirtualCurrency:
            if vcRule.awardFrequency == VirtualCurrencyAwardFrequency.justOnce:
                searchObject = 0
            else:
                searchObject = eventEntry.objectID
            if StudentVirtualCurrency.objects.filter(studentID = student.studentID, objectID = searchObject, vcRuleID = vcRule).exists():
                # Student was already awarded this virtual currency award for this object and this rule.  Do nothing.
                return
                        
        studVCRec = StudentVirtualCurrency()
        studVCRec.studentID = student.studentID
        if vcRule.awardFrequency == VirtualCurrencyAwardFrequency.justOnce:
            studVCRec.objectID = 0
        else:
            studVCRec.objectID = eventEntry.objectID
        studVCRec.vcRuleID = vcRule
        studVCRec.save()
        
        if actionID == Action.increaseVirtualCurrency:
            # Increase the student virtual currency amount
            student.virtualCurrencyAmount += vcRuleAmount
            student.save()
            notify.send(None, recipient=studentID.user, actor=studentID.user, verb='You Won '+str(vcRuleAmount)+' virtual currency', nf_type='Increase VirtualCurrency')
            return
    
        if actionID == Action.decreaseVirtualCurrency:
            # Decrease the student virtual currency amount
            if student.virtualCurrencyAmount >= vcRuleAmount:
                student.virtualCurrencyAmount -= vcRuleAmount 
                instructorCourse = InstructorRegisteredCourses.objects.filter(courseID=courseID).first()
                instructor = instructorCourse.instructorID
                notify.send(None, recipient=instructor, actor=studentID.user, verb= studentID.user.first_name +' '+studentID.user.last_name+ ' spent '+str(vcRuleAmount)+' virtual currency', nf_type='Decrease VirtualCurrency')
            else:
                #Notify that this purchase did not go through                        #### STILL TO BE IMPLEMENTED
                print('this purchase did not go through')
            student.save()
            return
