'''
Created on April 12, 2017

@author: Christo Dichev
'''

from django.contrib.auth.models import User
from django.shortcuts import redirect

from Instructors.views.utils import initialContextDict
from Instructors.models import UploadedFiles
from Instructors.constants import anonymous_avatar
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck  

import logging
logger = logging.getLogger(__name__)

def process_file(filename):
    ls = []
    fp = open(filename)
    lineCount = 0 # Used to keep count of the lines we have to skip the first two interations of the loop
    
    for line in fp:
        if(lineCount >= 2):
            # #line = line.replace('"', '')
            line = line.strip()
            names = line.split(',')
            ls.append((names[1].lstrip("\""), names[0].lstrip("\""),  names[3].lstrip(), names[4]))
        lineCount += 1
    print(ls)
    return ls

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def importStudents(request):
    
    # IMPORTANT: We presume that since the instructor is getting the file from a university system, 
    # there will be only two cases: 1/ the student is not in OneUp; 2/ The student is in OneUp but not in this course  
              
    context_dict, currentCourse = initialContextDict(request)
    context_dict['usertype'] = 'Student'
    context_dict['message'] = ''
    ccparams = context_dict['ccparams']

    if request.method == 'POST' and len(request.FILES) != 0:     
        studentslistFile = request.FILES['studentslist']
        studentslistFileName = studentslistFile.name 
        print(studentslistFileName)
          
        upfile = UploadedFiles() 
        upfile.uploadedFile = studentslistFile        
        upfile.uploadedFileName = studentslistFileName
        upfile.uploadedFileCreator = request.user
        upfile.save()
    
    students = process_file(upfile.uploadedFile.name)
    
    for studentData in students:
        uname = studentData[3] # The sutdnt username without @rams
        email = studentData[3] + "@rams.wssu.edu"
        pword = studentData[2]  # The SIS User ID found in the canvas csv file
        print("psswd", pword)
        
        # Check if student is in the system already
        users = User.objects.filter(email = email)
        if users:
            #the student is in the system, get it
            user = users[0] 
            student = Student.objects.get(user = user)              
                       
        else:
        # the student is not in the system, create a user/student       
            user = User.objects.create_user(uname, email, pword)
            user.first_name = studentData[0][1:-1]
            user.last_name = studentData[1]
            user.save()
            
            student = Student()
            student.user = user
            student.universityID = email
            student.save()
        
        # register the student for this course
        if not StudentRegisteredCourses.objects.filter(courseID=currentCourse,studentID=student): # keeps us from registering the same students over and over
            studentRegisteredCourses = StudentRegisteredCourses()
            studentRegisteredCourses.studentID = student
            studentRegisteredCourses.courseID = currentCourse
            studentRegisteredCourses.avatarImage = anonymous_avatar
            if ccparams.virtualCurrencyAdded:
                studentRegisteredCourses.virtualCurrencyAmount += int(ccparams.virtualCurrencyAdded)
            studentRegisteredCourses.save()
            
            logger.debug('[POST] Created New Student With VC Amount: ' + str(studentRegisteredCourses.virtualCurrencyAmount))

            # Create new Config Parameters
            scparams = StudentConfigParams()
            scparams.courseID = currentCourse
            scparams.studentID = student
            scparams.save()
        
    return redirect('createStudentListView')
            
            
