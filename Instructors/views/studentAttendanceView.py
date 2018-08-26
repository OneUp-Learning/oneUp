'''
Created on 8/23/18

@author: GGM
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Students.models import StudentRegisteredCourses, StudentAttendance, Student
from Instructors.views.utils import initialContextDict, utcDate,localizedDate
from django.contrib.auth.models import User
from Instructors.models import Courses
import datetime

@login_required
def createContextForStudentAttendance(request, context_dict, currentCourse): 
    sts_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    attendanceRecords = []
    
    if request.POST.get('rollDate') == None:
        context_dict["rollDate"] = datetime.datetime.today().strftime('%Y-%m-%d')
        getRollByDate(request, context_dict,attendanceRecords)
        
    if request.POST.get('rollDate'): 
        context_dict["rollDate"] = request.POST.get('rollDate')
        getRollByDate(request, context_dict,attendanceRecords)  
        
    if request.POST.getlist('present[]'):
        context_dict['present[]'] = request.POST.getlist('present[]')
        print(context_dict['present[]'])
        updateAttendaceRecord(request, context_dict)
        createAttendanceRecords(context_dict['present[]'], context_dict ,currentCourse)
    
    if request.POST.getlist('noCheckboxes'): 
        context_dict['noCheckboxes'] = request.POST.getlist('noCheckboxes')
        print(context_dict['noCheckboxes'])
        if(context_dict['noCheckboxes'] == ['false']):
            print("ran")
            updateAttendaceRecord(request, context_dict)
        
    if request.GET:
        getRollByDate(request, context_dict,attendanceRecords) 
        
    return context_dict

    
@login_required
def studentAttendance(request):

    context_dict, currentCourse = initialContextDict(request)
    context_dict = createContextForStudentAttendance(request, context_dict, currentCourse)
    
    return render(request,'Instructors/StudentAttendance.html', context_dict)  

def getRollByDate(request, context_dict,attendanceRecords):
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
    
    
    for studentId in student_ID:
        studentAttendance = StudentAttendance.objects.filter(courseID = request.session['currentCourseID'], timestamp=context_dict["rollDate"]+" 00:00:00", studentID=studentId).first()
        if studentAttendance != None:
            attendanceRecords.append(studentAttendance)
        if not studentAttendance:
            isPresent.append("") 
        else:
            isPresent.append("checked")
        
    context_dict["class"] = zip(student_ID, student_Avatars, student_Names, isPresent)
    
def createAttendanceRecords(presentStudents, context_dict, currentCourse):
    for student in presentStudents:
        studentRecord = StudentAttendance()
        user = User.objects.get(username=student)
        studentID = Student.objects.get(user=user)
        studentRecord.studentID = studentID
        studentRecord.isPresent = True
        studentRecord.courseID = currentCourse
        studentRecord.timestamp = context_dict["rollDate"]+" 00:00:00"
        studentRecord.save()  
def updateAttendaceRecord(request,context_dict):
    attendanceRecords = StudentAttendance.objects.filter(courseID = request.session['currentCourseID'], timestamp=context_dict["rollDate"]+" 00:00:00")
    print("attendanceRecords")
    print(attendanceRecords)
    for record in attendanceRecords:
        print("delete")
        print(record)
        studentRecord = StudentAttendance.objects.get(studentAttendanceID=record.studentAttendanceID).delete()
    attendanceRecords = []    
    
        