'''
Created on 8/28/18

@author: GGM
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Students.models import StudentRegisteredCourses, StudentAttendance, Student
from Instructors.views.utils import initialContextDict
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from django.utils.dateparse import parse_date
from django.utils.timezone import localtime, now

@login_required
def studentAttendanceReportView(request):
    context_dict, classID = initialContextDict(request)
    #if we have request get, get the roll by the current date(today)
    #we must parse the date to get it into a special format for querying the database
    if request.method == 'GET':
        context_dict["firstDate"] = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')
        context_dict["firstDateParsed"] = parse_date(context_dict["firstDate"])
        
        context_dict["secondDate"] = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')
        context_dict["secondDateParsed"] = parse_date(context_dict["secondDate"])
        
        context_dict = getRollByDate(request, context_dict) 
        return render(request, 'Instructors/StudentAttendanceReport.html', context_dict)    
       
    if request.method == 'POST':
        #if roll date is there, set it to the context dictionary and get the roll by date    
        if 'firstDate' in request.POST: 
            context_dict["firstDate"] = request.POST['firstDate']
            context_dict["secondDate"] = request.POST['secondDate']
            
            context_dict["firstDateParsed"] = parse_date(request.POST['firstDate'])
            context_dict["secondDateParsed"] = parse_date(request.POST['secondDate'])
            context_dict = getRollByDate(request, context_dict)
            return render(request, 'Instructors/StudentAttendanceReport.html', context_dict)        
#loads in the student objects if any, in studentattendance table
#and get the data of the student if they were here or not
def getRollByDate(request, context_dict):
    student_Names = []
    student_Avatars = []
    student_ID = []
    
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID'])
    for entry in studentCourse:
        user = User.objects.get(username=entry.studentID)
        studentID = Student.objects.get(user=user)
        student_ID.append(studentID)
        student_Avatars.append(entry.avatarImage)
        student_Names.append((entry.studentID).user.get_full_name())
    isPresent = [] 
    
    context_dict["students"] = student_ID
    studentAttendance = StudentAttendance.objects.filter(courseID = request.session['currentCourseID'], timestamp__range=(context_dict["firstDateParsed"],context_dict["secondDateParsed"]))
    #selected dates has the content for  iterating and querying by dates
    context_dict["selectedDates"] = generateDatesListForIteration(context_dict["firstDateParsed"], context_dict["secondDateParsed"])

    ##gets the dates, and iterate over the student IDS, then iterate over the dates to find out if a record exists
    ##if not, append false, if they have a record check present or not present
    studentAttendance = list(studentAttendance)
    dates = list(context_dict["selectedDates"])
    for id in student_ID:
        studentPresenceOnDatesList = []
        for date in dates:
            student = StudentAttendance.objects.filter(courseID = request.session['currentCourseID'], timestamp=date, studentID=id)
            if not student:
                studentPresenceOnDatesList.append("false")
            else:
                student = list(student)
                if student[0].isPresent == True:
                    studentPresenceOnDatesList.append("true")
                else:
                    studentPresenceOnDatesList.append("false")
                    
        isPresent.append(studentPresenceOnDatesList) 
        
    context_dict["class"] = zip(student_ID, student_Avatars, student_Names, isPresent)
    context_dict["Dates"] = generateDatesList(context_dict["firstDateParsed"], context_dict["secondDateParsed"])
    return context_dict

#what is used to iterate over the dates
#we need this form because django requires a special form for the dates
def generateDatesListForIteration(startDate, endDate):
    dates = []
    step = timedelta(days=1)
    while startDate <= endDate:
        dates.append(str(startDate))
        startDate += step 
    return dates

##what is used to display the dates on the page
def generateDatesList(startDate, endDate):
    dates = []
    step = timedelta(days=1)
    while startDate <= endDate:
        dates.append(str(startDate.month) +"/"+str(startDate.day))
        startDate += step 
    return dates