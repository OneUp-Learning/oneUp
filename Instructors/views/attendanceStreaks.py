#  GGM
#  12/28/2018

from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from Students.views.utils import studentInitialContextDict
from Badges.models import LeaderboardsConfig
from oneUp.decorators import instructorsCheck
from Badges.models import CourseConfigParams 
from Instructors.models import AttendanceStreak
from Badges.models import Conditions, Rules, RuleEvents, ActionArguments, VirtualCurrencyRuleInfo
import json, datetime, ast, re
from argparse import Action
from Students.models import StudentRegisteredCourses


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')  
def attendanceStreaks(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    
    if AttendanceStreak.objects.filter(courseID=currentCourse).exists():
        streak = AttendanceStreak.objects.filter(courseID=currentCourse)[0]
    else:
        streak = AttendanceStreak()
        streak.courseID = currentCourse
        streak.save()
    
    if Rules.objects.filter(courseID=currentCourse, awardFrequency=1100).exists():
        rule = Rules.objects.filter(courseID=currentCourse)[0]
    else:
        condition = Conditions()
        condition.operation =  '='
        condition.courseID = currentCourse
        condition.operand1Type = 1005
        condition.operand1Value = 950
        
        condition.operand2Type = 1001
        condition.operand2Value = streak.streakLength
        condition.save()
        
        rule = Rules()
        rule.conditionID = condition
        rule.courseID = currentCourse
        rule.actionID =  710
        rule.awardFrequency = 1100
        rule.save()
        
        ruleEvent = RuleEvents()
        ruleEvent.rule = rule
        ruleEvent.event = 870
        ruleEvent.save()
        
        actionArgument = ActionArguments()
        actionArgument.ruleID = rule
        actionArgument.sequenceNumber = 1
        actionArgument.argumentValue = 5
        actionArgument.save()
        
        vcRuleInfo = VirtualCurrencyRuleInfo()
        vcRuleInfo.vcRuleName = "Attendance Streak"
        vcRuleInfo.vcRuleDescription = "Streaks"
        vcRuleInfo.vcRuleType = True  
        vcRuleInfo.vcRuleAmount = 5
        vcRuleInfo.courseID = currentCourse
        vcRuleInfo.ruleID = rule
        vcRuleInfo.save()
        
        ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
        if StudentRegisteredCourses.objects.filter(courseID=currentCourse).exists():
            studentRegisteredCoursesRecords = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
            for studentRegisteredCoursesRecord in studentRegisteredCoursesRecords:
                studentRegisteredCoursesRecord.attendanceStreakStartDate = ccparams.courseStartDate
                studentRegisteredCoursesRecord.save()
        
               
    if request.method == 'GET':
        print("get")
        ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
        if ccparams:
            context_dict['courseStartDate'] = ccparams.courseStartDate
            context_dict['courseEndDate'] = ccparams.courseEndDate
            
            dayDict = {  # dict that converts from number day to text date
               "Monday": 0 ,
               "Tuesday":1,
               "Wednesday":2,
               "Thursday":3,
               "Friday":4,
               "Saturday":5,
               "Sunday":6
            }
            
            d = ccparams.courseStartDate
            delta = datetime.timedelta(days=1)
            
            if streak.daysofWeek:
                streakDays = ast.literal_eval(streak.daysofWeek)
                streakDays = [int(i) for i in streakDays]
                streak_calendar_days = []
                while d <= ccparams.courseEndDate:
                    if d.weekday() in streakDays:
                        streak_calendar_days.append(d.strftime("%Y-%m-%d"))
                    d += delta
                daysForCalendar = generateEventsForStreakDates(streak_calendar_days, streak.daysDeselected)
                context_dict['event'] = daysForCalendar[0]
                context_dict['eventCheckboxDays'] = daysForCalendar[1]
            else:
                streakDays = ""
                context_dict['event'] = "[]"
                context_dict['eventCheckboxDays'] = "[]"
            
            daysDeselected = datesUnSelectedFromDatabase(streak.daysDeselected)
            
            context_dict['eventCheckboxDaysUnselected'] = daysDeselected
        context_dict['streak'] = streak
        
        return render(request, 'Instructors/AttendanceStreaks.html', context_dict)   
    if request.method == 'POST':
        
        print("post")
        streak.courseID = currentCourse
            
        if 'daysOfWeek[]' in request.POST:
            print("request.post.getlistcheckboc", request.POST.getlist('daysOfWeek[]'))
            checkboxResult = request.POST.getlist('daysOfWeek[]')
            if not checkboxResult:
                streak.daysofWeek = []
            else:
                streak.daysofWeek = request.POST.getlist('daysOfWeek[]')
            
        if 'streakLength' in request.POST:
            streak.streakLength = request.POST['streakLength']
           
            if Conditions.objects.filter(courseID=currentCourse, operand1Type=1005, operand1Value=950, operation="=").exists():
                condition = Conditions.objects.filter(courseID=currentCourse, operand1Type=1005, operand1Value=950, operation="=")[0]
                condition.operand2Value = streak.streakLength
                condition.save()
            
        datesFromCalendarProcessed = []
        if 'dates[]' in request.POST:
            datesFromCalendar = request.POST.getlist('dates[]')
            print("datesfromcalendar", datesFromCalendar)
        
        if 'calendarDaysCheckedList' in request.POST:
            checkedCalendarDays = filterOutDuplicatesFromCalendar(request.POST.getlist('calendarDaysCheckedList'))
            print("checkedcalendardays", str(checkedCalendarDays).split(","))
            
        if 'calendarDaysUncheckedList' in request.POST:
            uncheckedCalendarDays = filterOutDuplicatesFromCalendar(request.POST.getlist('calendarDaysUncheckedList'))
            print('calendarDaysUncheckedList', uncheckedCalendarDays)
            streak.daysDeselected = uncheckedCalendarDays
        streak.save()   

        return redirect('attendanceStreaks')

    
def generateEventsForStreakDates(streak_dates, excluded_Dates):
    eventDays = []
    events = []
    filteredStreakDays = []
    for date in streak_dates:
        if date not in excluded_Dates:
            filteredStreakDays.append(date)
    for filtered_date in filteredStreakDays:
        event = {
            'title': 'Streak',
            'start': str(filtered_date)
            
            }
        events.append(event)
    eventDays = filteredStreakDays
    return (events, eventDays)
def datesUnSelectedFromDatabase(dates):
    daysDeselected = dates.split(",")
    daysDeselectedCleanedString = []
    for dayDeselected in daysDeselected:
        daysDeselectedCleanedString.append( re.sub("(\['|'])","",dayDeselected))
    print("days deselected", daysDeselected)
    return daysDeselectedCleanedString

def filterOutDuplicatesFromCalendar(datesList):
    print("filtered")
    print(list(dict.fromkeys(datesList)))
    return list(dict.fromkeys(datesList))
