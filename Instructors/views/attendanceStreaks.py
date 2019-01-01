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
import json, datetime, ast, re


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')  
def attendanceStreaks(request):
    context_dict, currentCourse = studentInitialContextDict(request)
    
    streak = AttendanceStreak.objects.filter(courseID=currentCourse)
    if streak:
        streak = streak[0]
    else:
        streak = AttendanceStreak()   
        
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
            
        datesFromCalendarProcessed = []
        if 'dates[]' in request.POST:
            datesFromCalendar = request.POST.getlist('dates[]')
            print("datesfromcalendar", datesFromCalendar)
        
        if 'calendarDaysCheckedList' in request.POST:
            checkedCalendarDays = request.POST.getlist('calendarDaysCheckedList')
            print("checkedcalendardays", str(checkedCalendarDays).split(","))
            
        if 'calendarDaysUncheckedList' in request.POST:
            uncheckedCalendarDays = request.POST.getlist('calendarDaysUncheckedList')
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
    print("filtered days", filteredStreakDays)
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
