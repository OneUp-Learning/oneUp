'''
Created on April 12, 2017

@author: Christo Dichev
'''

from django.contrib.auth.models import User
from django.shortcuts import redirect

from Instructors.models import Courses
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses
from django.contrib.auth.decorators import login_required

@login_required



def process_file(filename):
    ls = []
    fp = open(filename)
    
    for line in fp:
        line = line.replace('"', '')
        names = line.split(',',3)
        ls.append((names[1], names[0],  names[2]+'@rams.wssu.edu',names[2] ))
    return ls[1:]


def importStudents(request):
    
    context_dict = { }
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
        currentCourse = 1
    
    studentslistFile = request.FILES['studentslist']
    studentslistFileName = studentslistFile.name   
    filePath = '../oneUpER/media/textFiles/'+ studentslistFileName
    students = process_file(filePath)
    for studentData in students:
        uname = studentData[3]
        
        email = studentData[2]
        pword = uname +'7' # has to be change by the instructor or the student
        user = User.objects.create_user(uname, email, pword)
        user.first_name = studentData[0]
        user.last_name = studentData[1]
        user.save()
        
        student = Student()
        student.user = user
        student.universityID = email
        student.save()
        
        studentRegisteredCourses = StudentRegisteredCourses()
        studentRegisteredCourses.studentID = student
        studentRegisteredCourses.courseID = currentCourse
        studentRegisteredCourses.avatarImage = anonymous_avatar
        studentRegisteredCourses.save()
        
    return redirect('createStudentListView')
            
            
