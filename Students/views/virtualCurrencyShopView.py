from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from Students.models import StudentRegisteredCourses, StudentVirtualCurrencyTransactions
from Students.views.utils import studentInitialContextDict

from Badges.models import Rules, ActionArguments
from Badges.enums import Action, Event, ObjectTypes
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
            return Rules.objects.filter(ruleevents__event=event, courseID=currentCourse)

        # We assume that if a rule decreases virtual currency, it is a
        # buy rule.  This function assumes that virtual currency penalty
        # rules have already been screened out.  A more robust test
        # would be needed if used in a different context.        
        def checkIfRuleIsBuyRule(rule):
            return rule.actionID == Action.decreaseVirtualCurrency
        
        def getAmountFromBuyRule(rule):
            if ActionArguments.objects.filter(ruleID=rule,sequenceNumber=1).exists:
                return int(ActionArguments.objects.get(ruleID=rule, sequenceNumber=1).argumentValue)
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
            if event in [Event.instructorHelp, Event.buyAttempt, Event.extendDeadlineHW, Event.extendDeadlineLab, Event.replaceLowestAssignGrade, Event.buyExtraCreditPoints]:
                defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
                currentTime = utcDate()
                challenges = Challenges.objects.filter(courseID=currentCourse, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))
                activites = Activities.objects.filter(courseID=currentCourse)
                
                for challenge in challenges:
                    challQuestions = ChallengesQuestions.objects.filter(challengeID=challenge)
                    # Only pick challenges that have questions assigned to them
                    if challQuestions:
                        challenges_id.append(challenge.challengeID)
                        challenges_name.append(challenge.challengeName)
                for activity in activites:
                    challenges_id.append(activity.activityID)
                    challenges_name.append(activity.activityName)
                    
                if len(challenges_id) == 0:
                    return None
                return zip(challenges_id, challenges_name) 
            else:
                return None
                   
        
        if request.method == "GET":
            # For an event, find all the rules in the current course which
            # trigger from that event
            
            buyOptionList = [Event.buyAttempt,Event.instructorHelp, Event.extendDeadlineHW,Event.extendDeadlineLab,Event.replaceLowestAssignGrade, Event.buyTestTime, Event.buyExtraCreditPoints,
                             Event.getDifferentProblem, Event.getSurpriseAward, Event.getCreditForOneTestProblem]
            buyOptionEnabled = {}
            buyOptionCost = {}
            for buyOpt in buyOptionList:
                buyOptionEnabled[buyOpt],buyOptionCost[buyOpt] = getBuyAmountForEvent(buyOpt) 
    
            enabledBuyOptions = []
            for buyOpt in buyOptionList:
                if buyOptionEnabled[buyOpt]:
                    enabledBuyOptions.append(buyOpt)
            
            
            request.session['buyoptions']=enabledBuyOptions
            
            buyOptions = []
            index = 0
            for buyOpt in enabledBuyOptions:
                event = Event.events[buyOpt]
                buyOptions.append({'id':index,
                                   'cost':buyOptionCost[buyOpt],
                                   'name':event['name'],
                                   'displayName':event['displayName'],
                                   'description':event['description'],
                                   'challenges':getChallengesForEvent(buyOpt)})
                index += 1
                            
            context_dict['buyOptions']=buyOptions
            context_dict['buyOptions2']=buyOptions
            context_dict['numBuyOptions']=len(buyOptions)
            context_dict['studentVirtualCurrency'] = currentStudentCurrencyAmmount
            
            return render(request,"Students/VirtualCurrencyShop.html",context_dict)
                
        elif request.method == "POST":
            # Here we should make things happen.
            # TODO: Assign object Id to be challenge id selected for the item bought
            enabledBuyOptions = request.session['buyoptions']
            i = 0
            for buyOption in enabledBuyOptions:
                quantity = request.POST['buyOptionQuantity'+str(i)]
                for j in range(0, int(quantity)):
                    # Object ID needs to be challenge ID for certain events (Event.instructorHelp, Event.buyAttempt,Event.extendDeadline, Event.dropLowestAssignGrade, Event.buyExtraCreditPoints)
                    studentVCTransaction = StudentVirtualCurrencyTransactions()
                    studentVCTransaction.student = student
                    studentVCTransaction.course = currentCourse
                    
                    if buyOption in [Event.instructorHelp, Event.buyAttempt,Event.extendDeadlineHW, Event.extendDeadlineLab, Event.replaceLowestAssignGrade, Event.buyExtraCreditPoints, Event.buyTestTime, Event.getDifferentProblem, Event.getCreditForOneTestProblem]:
                        event = Event.events[buyOption]
                        studentVCTransaction.studentEvent = register_event(buyOption, request, student, int(request.POST['challengeFor'+event['name']]))
                        studentVCTransaction.objectType = ObjectTypes.challenge
                        studentVCTransaction.objectID = int(request.POST['challengeFor'+event['name']])
                        studentVCTransaction.status = 'Requested'
                        studentVCTransaction.save()
                    else:
                        studentVCTransaction.studentEvent = register_event(buyOption, request, student, 0)
                        studentVCTransaction.objectType = ObjectTypes.form
                        studentVCTransaction.objectID = 0
                        studentVCTransaction.status = 'Requested'
                        studentVCTransaction.save()
                i += 1
                
            return redirect("/oneUp/students/Transactions.html")

            
                
                
                
                
            
