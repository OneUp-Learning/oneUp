from django.shortcuts import render

from django.template import RequestContext
from django.shortcuts import render, redirect

from Instructors.models import Answers, CorrectAnswers, MatchingAnswers, Courses, Challenges, StaticQuestions
from Students.models import Student, StudentRegisteredCourses, StudentChallengeQuestions, StudentChallengeAnswers, MatchShuffledAnswers, StudentRegisteredCourses

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from Badges.models import Rules, ActionArguments
from Badges.enums import Action, Event

from Badges.events import register_event

@login_required
def virtualCurrencyShopView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username       
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        student = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage          
        
        if request.method == "GET":
            # For an event, find all the rules in the current course which
            # trigger from that event
            def getRulesForEvent(event):
                return Rules.objects.filter(ruleevents__event=event,courseID=currentCourse)
    
            # We assume that if a rule decreases virtual currency, it is a
            # buy rule.  This function assumes that virtual currency penalty
            # rules have already been screened out.  A more robust test
            # would be needed if used in a different context.        
            def checkIfRuleIsBuyRule(rule):
                return rule.actionID == Action.decreaseVirtualCurrency
            
            def getAmountFromBuyRule(rule):
                return int(ActionArguments.objects.get(ruleID=rule,sequenceNumber=1).argumentValue)
            
            # We just find the first one.  This should generally be fine
            # since there should be at most one.
            def getFirstBuyRule(ruleList):
                for rule in ruleList:
                    if checkIfRuleIsBuyRule(rule):
                        return rule
                return None
            
            def getBuyAmountForEvent(event):
                #print(Event.events[event]['displayName'])
                rules = getRulesForEvent(event)
                #print(rules)
                buyRule = getFirstBuyRule(rules)
                if buyRule is None:
                    return (False,0)
                else:
                    return (True,getAmountFromBuyRule(buyRule))
            
            buyOptionList = [Event.buyAttempt,Event.buyHint, Event.extendDeadline,Event.dropLowestAssignGrade, Event.chooseBackgroundForYourName, Event.chooseDashboardBackground, Event.chooseLabPartner,
                             Event.chooseProjectPartner, Event.getDifferentProblem, Event.getSurpriseAward, Event.seeClassAverage, Event.uploadOwnAvatar]
            buyOptionEnabled = {}
            buyOptionCost = {}
            for buyOpt in buyOptionList:
                buyOptionEnabled[buyOpt],buyOptionCost[buyOpt] = getBuyAmountForEvent(buyOpt) 
                #print(getBuyAmountForEvent(buyOpt))
    
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
                                   'description':event['description']})
                index += 1
                
            student = StudentRegisteredCourses.objects.get(studentID = student, courseID = int(request.session['currentCourseID']))
            
            context_dict['buyOptions']=buyOptions
            context_dict['buyOptions2']=buyOptions
            context_dict['numBuyOptions']=len(buyOptions)
            context_dict['studentVirtualCurrency'] = student.virtualCurrencyAmount
            
            return render(request,"Students/VirtualCurrencyShop.html",context_dict)
                
        elif request.method == "POST":
            # Here we should make things happen.
            
            enabledBuyOptions = request.session['buyoptions']
            i = 0
            for buyOption in enabledBuyOptions:
                quantity = request.POST['buyOptionQuantity'+str(i)]
                for j in range(0, int(quantity)):
                    register_event(buyOption, request, student, 0) # ObjectID has to be null?
                i += 1

            #TODO: Actually deliver the rewards.
            # This code only triggers the events which should take away the virtual currency
            
            return redirect("/oneUp/students/VirtualCurrencyShop.html")
            
                
                
                
                
            