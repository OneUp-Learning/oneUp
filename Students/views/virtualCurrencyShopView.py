from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions, StudentChallenges, StudentActivities, StudentEventLog
from Students.views.utils import studentInitialContextDict

from Badges.models import VirtualCurrencyRuleInfo, ActionArguments, RuleEvents, VirtualCurrencyCustomRuleInfo
from Badges.enums import Action, Event, ObjectTypes, dict_dict_to_zipped_list
from Badges.events import register_event
import logging
import copy

@login_required
def virtualCurrencyShopView(request):
    logger = logging.getLogger(__name__)
    
    context_dict,currentCourse = studentInitialContextDict(request)
 
    if 'currentCourseID' in request.session:  

        student = context_dict['student']
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)              
        currentStudentCurrencyAmmount = st_crs.virtualCurrencyAmount          
        # RULE BASED VC NOT USED
        def getRulesForEvent(event):
            return VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, ruleID__ruleevents__event=event, courseID=currentCourse)

        # We assume that if a rule decreases virtual currency, it is a
        # buy rule.  This function assumes that virtual currency penalty
        # rules have already been screened out.  A more robust test
        # would be needed if used in a different context.   
        # RULE BASED VC NOT USED     
        def checkIfRuleIsBuyRule(rule):
            return rule.ruleID.actionID == Action.decreaseVirtualCurrency
        # RULE BASED VC NOT USED
        def getAmountFromBuyRule(rule):
            if ActionArguments.objects.filter(ruleID=rule.ruleID,sequenceNumber=1).exists:
                return int(ActionArguments.objects.get(ruleID=rule.ruleID, sequenceNumber=1).argumentValue)
            else:
                return 0
        
        # We just find the first one.  This should generally be fine
        # since there should be at most one.
        # RULE BASED VC NOT USED
        def getFirstBuyRule(ruleList):
            for rule in ruleList:
                if checkIfRuleIsBuyRule(rule):
                    return rule
            return None
        # RULE BASED VC NOT USED
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
        # RULE BASED VC NOT USED
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
                challenges = Challenges.objects.filter(courseID=currentCourse, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime))
                activites = Activities.objects.filter(courseID=currentCourse).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime))
                
                for challenge in challenges:
                    studentChallenges = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=challenge)
                    challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
                    # Only pick challenges that have questions assigned to them and is graded
                    if challQuestions and studentChallenges:
                        challenges_id.append(challenge.challengeID)
                        challenges_name.append(challenge.challengeName)
                for activity in activites:
                    #studentActivities = StudentActivities.objects.filter(studentID=student, courseID=currentCourse,activityID=activity)
                    # Only pick activities that are graded
                    if activity.isGraded == True:
                        challenges_id.append(activity.activityID)
                        challenges_name.append(activity.activityName)
                    
                if len(challenges_id) == 0:
                    return None
                return zip(challenges_id, challenges_name) 
            else:
                return 0

        # Gets all the serious challenges and graded activities
        def getChallengesForShop(request):
            from Instructors.models import Challenges , ChallengesQuestions, Activities
            from Instructors.constants import default_time_str
            from Instructors.views.utils import utcDate, localizedDate
            from django.db.models import Q
            from datetime import datetime
            


            challenges_id = []
            challenges_name = []

            defaultTime = localizedDate(request, default_time_str, "%m/%d/%Y %I:%M %p")
            print("Default Time: {}".format(defaultTime))
            currentTime = localizedDate(request, str(datetime.utcnow().replace(microsecond=0)), "%Y-%m-%d %H:%M:%S")
            print("Current Time: {}".format(currentTime))
            challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime))
            activites = Activities.objects.filter(courseID=currentCourse, isGraded=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime))
            
            for challenge in challenges:
                challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
                # Only pick challenges that have questions assigned to them
                if challQuestions:
                    challenges_id.append(challenge.challengeID)
                    challenges_name.append(challenge.challengeName)
            for activity in activites:
                #studentActivities = StudentActivities.objects.filter(studentID=student, courseID=currentCourse,activityID=activity)
                # Only pick activities that are graded

                challenges_id.append(activity.activityID)
                challenges_name.append(activity.activityName)
                
            if len(challenges_id) == 0:
                return None
            return zip(challenges_id, challenges_name)   
        
        if request.method == "GET":
            buyOptions = []
            # RULE BASED VC NOT USED
            # rules = VirtualCurrencyRuleInfo.objects.filter(vcRuleType=False, courseID = currentCourse)
            # eventObjects= dict_dict_to_zipped_list(Event.events,['index','displayName', 'description','isVirtualCurrencySpendRule'])  
            # index = 0
            # for i, eName, eDescription, eIsVirtualCurrencySpendRule in eventObjects:
            #     # disabled adjustment event(861) for now since teacher can adjust a student challenge grade and we don’t have a way to restrict number of purchases in course shop :( 
            #     if eIsVirtualCurrencySpendRule:
            #         for rule in rules:
            #             ruleEvent = RuleEvents.objects.get(rule = rule.ruleID)
            #             if ruleEvent.event == i:
            #                 buyOptions.append({'id':index,
            #                        'eventID': i,
            #                        'cost':getAmountFromBuyRule(rule),
            #                        'name':eName,
            #                        'displayName':rule.vcRuleName,
            #                        'description':rule.vcRuleDescription,
            #                        'challenges':getChallengesForEvent(i),
            #                        'limit':rule.vcRuleLimit,
            #                        'remaining': 0})
            #                 break   
            #     index += 1

            vc_rules = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=False, courseID = currentCourse)
            challenges = getChallengesForShop(request)
            for rule in vc_rules:
                buyOptions.append({'id':rule.vcRuleID, 'cost': rule.vcRuleAmount, 'name': rule.vcRuleName, 'displayName': rule.vcRuleName, 
                'description': rule.vcRuleDescription, 'challenges': copy.deepcopy(challenges), 'limit': rule.vcRuleLimit, 'remaining': 0})

            # filter out the potential buy options if the student has went over the limit by looking at their transactions
            for buyOption in buyOptions:
                studentTransactions = StudentVirtualCurrencyTransactions.objects.filter(course = currentCourse, student = student, status__in = ['Requested', 'In Progress', 'Complete'], studentEvent__event = Event.spendingVirtualCurrency, studentEvent__objectID=buyOption['id'])
                if buyOption['limit'] == 0:
                    continue
                elif len(studentTransactions) >= buyOption['limit']:
                    buyOptions.remove(buyOption)
                else:
                    buyOption['remaining'] = abs(buyOption['limit'] - len(studentTransactions))
                    
            context_dict['buyOptions']=buyOptions
            request.session['buyoptions'] = [{'id': buyOption['id']} for buyOption in buyOptions]
            context_dict['numBuyOptions']=len(buyOptions)
            context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
            
            return render(request,"Students/VirtualCurrencyShop.html",context_dict)
                
        elif request.method == "POST":
            # Go through the buy options and complete the transactions
            enabledBuyOptions = request.session['buyoptions']
            total = 0
            for buyOption in enabledBuyOptions:
                quantity = request.POST['buyOptionQuantity'+str(buyOption['id'])]
                rule = VirtualCurrencyCustomRuleInfo.objects.filter(vcRuleType=False, courseID=currentCourse, vcRuleID=buyOption['id']).first()
                if rule:
                    total += int(quantity) * int(rule.vcRuleAmount)
                    for j in range(0, int(quantity)):
                        studentVCTransaction = StudentVirtualCurrencyTransactions()
                        studentVCTransaction.student = student
                        studentVCTransaction.course = currentCourse
                        
                        # RULE BASED VC NOT USED
                        # Object ID is challenge ID for certain events
                        # if buyOption['eventID'] in [Event.instructorHelp, Event.buyAttempt, Event.extendDeadlineHW, Event.extendDeadlineLab, Event.buyTestTime, Event.buyExtraCreditPoints,  Event.getDifferentProblem, Event.getCreditForOneTestProblem]:
                        #     event = Event.events[buyOption['eventID']]
                        #     studentVCTransaction.studentEvent = register_event(buyOption['eventID'], request, student, int(request.POST['challengeFor'+event['displayName']]))
                        #     studentVCTransaction.objectType = ObjectTypes.challenge
                        #     studentVCTransaction.objectID = int(request.POST['challengeFor'+event['displayName']])
                        #     studentVCTransaction.status = 'Requested'
                        #     studentVCTransaction.save()
                        # else:
                        
                        studentVCTransaction.studentEvent = register_event(Event.spendingVirtualCurrency, request, student, buyOption['id'])
                        print(request.POST['challengeFor'+rule.vcRuleName])
                        print(request.POST)
                        if request.POST['challengeFor'+rule.vcRuleName] == "none":
                            studentVCTransaction.objectType = ObjectTypes.virtualCurrencySpendRule
                            studentVCTransaction.objectID = buyOption['id']
                        else:
                            studentVCTransaction.objectType = ObjectTypes.challenge
                            studentVCTransaction.objectID = int(request.POST['challengeFor'+rule.vcRuleName])
                        studentVCTransaction.status = 'Requested'
                        studentVCTransaction.save()
            st_crs.virtualCurrencyAmount -= total
            st_crs.save()
            return redirect("/oneUp/students/Transactions.html")

            
                
                
                
                
            
