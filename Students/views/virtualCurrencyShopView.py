from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions, StudentChallenges, StudentActivities, StudentEventLog
from Students.views.utils import studentInitialContextDict

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments, RuleEvents
from Badges.enums import Action, Event, ObjectTypes, dict_dict_to_zipped_list
from Badges.events import register_event
import logging

@login_required
def virtualCurrencyShopView(request):
    logger = logging.getLogger(__name__)
    
    context_dict,currentCourse = studentInitialContextDict(request)
 
    if 'currentCourseID' in request.session:  

        student = context_dict['student']
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)              
        currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount          

        def getRulesForEvent(event):
            return VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, ruleID__ruleevents__event=event, courseID=currentCourse)

        # We assume that if a rule decreases virtual currency, it is a
        # buy rule.  This function assumes that virtual currency penalty
        # rules have already been screened out.  A more robust test
        # would be needed if used in a different context.        
        def checkIfRuleIsBuyRule(rule):
            return rule.ruleID.actionID == Action.decreaseVirtualCurrency
        
        def getAmountFromBuyRule(rule):
            if ActionArguments.objects.filter(ruleID=rule.ruleID,sequenceNumber=1).exists:
                return int(ActionArguments.objects.get(ruleID=rule.ruleID, sequenceNumber=1).argumentValue)
            else:
                return 0
        
        # We just find the first one.  This should generally be fine
        # since there should be at most one.
        def getFirstBuyRule(ruleList):
            for rule in ruleList:
                if checkIfRuleIsBuyRule(rule):
                    return rule
            return None
        
        def getBuyAmountForEvent(event):
            # print(Event.events[event]['displayName'])
            rules = getRulesForEvent(event)
            # print(rules)
            buyRule = getFirstBuyRule(rules)
            if buyRule is None:
                return (False, 0)
            else:
                return (True, getAmountFromBuyRule(buyRule))
        
        # Gets all the serious challenges for certain events that require the student to pick a challenge
        def getChallengesForEvent(event):
            from Instructors.models import Challenges , ChallengesQuestions, Activities
            from Instructors.constants import default_time_str
            from Instructors.views.utils import utcDate
            from django.db.models import Q

            
            challenges_id = []
            challenges_name = []

            if event in [Event.instructorHelp, Event.buyAttempt, Event.extendDeadlineHW, Event.extendDeadlineLab, Event.buyTestTime, Event.buyExtraCreditPoints,  Event.getDifferentProblem, Event.getCreditForOneTestProblem]:
                defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
                currentTime = utcDate()
                challenges = Challenges.objects.filter(courseID=currentCourse, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))
                activites = Activities.objects.filter(courseID=currentCourse)
                
                for challenge in challenges:
                    studentChallenges = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=challenge)
                    challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
                    # Only pick challenges that have questions assigned to them and is graded
                    if challQuestions and studentChallenges:
                        challenges_id.append(challenge.challengeID)
                        challenges_name.append(challenge.challengeName)
                for activity in activites:
                    studentActivities = StudentActivities.objects.filter(studentID=student, courseID=currentCourse,activityID=activity)
                    # Only pick activities that are graded
                    for sAct in studentActivities:
                        if sAct.graded == True:
                            challenges_id.append(activity.activityID)
                            challenges_name.append(activity.activityName)
                    
                if len(challenges_id) == 0:
                    return None
                return zip(challenges_id, challenges_name) 
            else:
                return 0
                   
        
        if request.method == "GET":
            buyOptions = []
            rules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, courseID = currentCourse)
            eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description','isVirtualCurrencySpendRule'])  
            index = 0
            for i, eName, eDescription, eIsVirtualCurrencySpendRule in eventObjects:
                # disabled adjustment event(861) for now since teacher can adjust a student challenge grade and we don’t have a way to restrict number of purchases in course shop :( 
                if eIsVirtualCurrencySpendRule:
                    for rule in rules:
                        ruleEvent = RuleEvents.objects.get(rule = rule.ruleID)
                        if ruleEvent.event == i:
                            buyOptions.append({'id':index,
                                   'eventID': i,
                                   'cost':getAmountFromBuyRule(rule),
                                   'name':eName,
                                   'displayName':rule.vcRuleName,
                                   'description':rule.vcRuleDescription,
                                   'challenges':getChallengesForEvent(i),
                                   'limit':rule.vcRuleLimit,
                                   'remaining': 0})
                            break   
                index += 1
            # filter out the potential buy options if the student has went over the limit by looking at their transactions
            for buyOption in buyOptions:
                studentTransactions = StudentVirtualCurrencyTransactions.objects.filter(course = currentCourse, student = student, status__in = ['Requested', 'In Progress', 'Completed'], studentEvent__event = buyOption['eventID'])
                if buyOption['limit'] == 0:
                    continue
                elif len(studentTransactions) >= buyOption['limit']:
                    buyOptions.remove(buyOption)
                else:
                    buyOption['remaining'] = abs(buyOption['limit'] - len(studentTransactions))
                    
            context_dict['buyOptions']=buyOptions
            request.session['buyoptions'] = [{'id': buyOption['id'], 'eventID': buyOption['eventID']} for buyOption in buyOptions]
            context_dict['numBuyOptions']=len(buyOptions)
            context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
            
            return render(request,"Students/VirtualCurrencyShop.html",context_dict)
                
        elif request.method == "POST":
            # Go through the buy options and complete the transactions
            enabledBuyOptions = request.session['buyoptions']
            for buyOption in enabledBuyOptions:
                quantity = request.POST['buyOptionQuantity'+str(buyOption['id'])]
                for j in range(0, int(quantity)):
                    studentVCTransaction = StudentVirtualCurrencyTransactions()
                    studentVCTransaction.student = student
                    studentVCTransaction.course = currentCourse
                    
                    # Object ID is challenge ID for certain events
                    if buyOption['eventID'] in [Event.instructorHelp, Event.buyAttempt, Event.extendDeadlineHW, Event.extendDeadlineLab, Event.buyTestTime, Event.buyExtraCreditPoints,  Event.getDifferentProblem, Event.getCreditForOneTestProblem]:
                        event = Event.events[buyOption['eventID']]
                        studentVCTransaction.studentEvent = register_event(buyOption['eventID'], request, student, int(request.POST['challengeFor'+event['displayName']]))
                        studentVCTransaction.objectType = ObjectTypes.challenge
                        studentVCTransaction.objectID = int(request.POST['challengeFor'+event['displayName']])
                        studentVCTransaction.status = 'Requested'
                        studentVCTransaction.save()
                    else:
                        event = Event.events[buyOption['eventID']]
                        studentVCTransaction.studentEvent = register_event(buyOption['eventID'], request, student, 0)
                        studentVCTransaction.objectType = ObjectTypes.form
                        studentVCTransaction.objectID = 0
                        studentVCTransaction.status = 'Requested'
                        studentVCTransaction.save()
            return redirect("/oneUp/students/Transactions.html")

            
                
                
                
                
            
