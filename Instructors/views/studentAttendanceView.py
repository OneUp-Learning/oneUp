'''
Created on 8/23/18

@author: GGM
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Students.models import StudentRegisteredCourses, StudentAttendance, Student
from Instructors.views.utils import initialContextDict
from django.contrib.auth.models import User
import datetime
from Instructors.views.challengeExportImportView import str2bool
from django.utils.timezone import localtime, now
from oneUp.decorators import instructorsCheck
from Badges.events import register_event    
from Badges.enums import Event 

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def studentAttendance(request):
    context_dict, currentCourse = initialContextDict(request)
    #if we have request get, get the roll by the current date(today)
    if request.method == 'GET':
        context_dict["rollDate"] = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')
        context_dict = getRollByDate(request, context_dict) 
        return render(request, 'Instructors/StudentAttendance.html', context_dict)    
       
    if request.method == 'POST':
        #if we have an array of present objects, get the roll and create attendance records
        if 'present[]' in request.POST:
            context_dict['rollDate'] = request.POST['rollDate']
            context_dict['present[]'] = request.POST.getlist('present[]')
            context_dict = getRollByDate(request, context_dict)   
            context_dict = createAttendanceRecords(context_dict['present[]'], context_dict ,currentCourse, request)
            return redirect('studentAttendance')   
        #if roll date is there, set it to the context dictionary and get the roll by date    
        if 'rollDate' in request.POST: 
            context_dict["rollDate"] = request.POST['rollDate']
            context_dict = getRollByDate(request, context_dict)
            return render(request, 'Instructors/StudentAttendance.html', context_dict)     
        else:#otherwise get the rollby date for today
            context_dict["rollDate"] = localtime(now()).strftime('%Y-%m-%d')
            context_dict = getRollByDate(request, context_dict)      
#loads in the student objects if any, in studentattendance table
#and get the data of the student if they were here or not
def getRollByDate(request, context_dict):
    student_First_Name = []
    student_Last_Name = []
    student_Avatars = []
    student_ID = []
    
    studentCourse = StudentRegisteredCourses.objects.filter(courseID = request.session['currentCourseID']).exclude(studentID__isTestStudent=True)
    for entry in studentCourse:
        user = User.objects.get(username=entry.studentID)
        studentID = Student.objects.get(user=user)
        student_ID.append(studentID)
        student_Avatars.append(entry.avatarImage)
        student_First_Name.append((entry.studentID).user.first_name)
        student_Last_Name.append((entry.studentID).user.last_name)
    isPresent = [] 
    
    context_dict["students"] = sorted(student_ID, key = lambda p: p.user.last_name)
    for studentId in student_ID:
        studentAttendance = StudentAttendance.objects.filter(courseID = request.session['currentCourseID'], timestamp=context_dict["rollDate"], studentID=studentId).first()
        if not studentAttendance:
            isPresent.append('false') 
        else:
            if studentAttendance.isPresent == True:
                isPresent.append('true')
            else:
                isPresent.append('false')
    zipped = zip(student_ID, student_Avatars, student_First_Name, student_Last_Name, isPresent)
    context_dict["class"] = sorted(zipped, key=lambda x: x[3])  
    return context_dict
    
#create the attendance record if they dont have a record    
def createAttendanceRecords(presentStudents, context_dict, currentCourse, request):
    studentsAndPresentData = zip(context_dict["students"], presentStudents)
    for student, present in studentsAndPresentData:
        createStudentAttendance(str2bool(present), currentCourse, context_dict, student)
        if present:
            register_event(Event.classAttendance, request, student, None)
        
    
    return context_dict
#create the records if they do not exist
#but also if they have a record, just set it to if present or not    
def createStudentAttendance(isPresent, currentCourse, context_dict, student):
    studentAttendance = StudentAttendance.objects.filter(courseID = currentCourse, timestamp=context_dict["rollDate"], studentID=student).first()
    if studentAttendance == None:
        if isPresent:
            studentRecord = StudentAttendance()
            user = User.objects.get(username=student)
            studentID = Student.objects.get(user=user)
            studentRecord.studentID = studentID
            studentRecord.isPresent = isPresent
            studentRecord.courseID = currentCourse
            studentRecord.timestamp = context_dict["rollDate"]
            studentRecord.save()
    else:
        if isPresent:    
            studentAttendance.isPresent = isPresent
            studentAttendance.save();
        else:
            studentAttendance.delete();
#true or false from the page becomes boolean true or false        
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")    