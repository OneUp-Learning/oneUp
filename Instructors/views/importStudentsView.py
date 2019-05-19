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

import logging, random, secrets
logger = logging.getLogger(__name__)

def generate_secure_password():
    ##generate a secure password
    token = secrets.token_urlsafe(16)
    token = token.replace('(i|l|1|L|o|0|O)', '')

    #if it has failed with length, make a new password until we reach 16
    while(len(token)< 10):
        token = secrets.token_urlsafe(16)
        token = token.replace('(i|l|1|L|o|0|O)', '')
    return token
def process_file(file_name, file_type_number):
    ##file type 0 is canvas, it is the default
    ##file type 1 is our OneUp csv files

    lines = []
    filePointer = open(file_name)
    lineCount = 0 # Used to keep count of the lines we have to skip the first two interations of the loop
    
    ##this is what reads for a canvas file
    if file_type_number == 0:
        for line in filePointer:
            if(lineCount >= 2):
                # #line = line.replace('"', '')
                line = line.strip()
                names = line.split(',')
                lines.append((names[1].lstrip("\""), names[0].lstrip("\""),  names[3].lstrip(), names[4]))
            lineCount += 1

    ##this is what reads our OneUp CSV
    if file_type_number == 1:
        for line in filePointer:
                line = line.replace('\"', '')
                line = line.strip()
                values = line.split(',')
                #first name, last name, email username
                lines.append((values[0].lstrip(),values[1].lstrip(), values[2].lstrip()))

    print("line",lines)
    return lines


def generate_student_data(username, email, password, student_data, currentCourse, ccparams, file_type_number):
            # Check if student is in the system already
            print("student data", student_data[0][1:-1],student_data[1],password)
            if User.objects.filter(username = username).exists():
                users_list = User.objects.filter(username = username)

                #the student is in the system, get it
                user = users_list[0] 
                student = Student.objects.get(user = user)              
                        
            else:
            # the student is not in the system, create a user/student       
                user = User.objects.create_user(username, email, password)

                #unfortunately must have special encoding for canvas
                if file_type_number == 0:
                    user.first_name = student_data[0][1:-1]
                else:
                    user.first_name = student_data[0]
                
                user.last_name = student_data[1]
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

        if 'file_number' in request.POST:
            file_type_number = int(request.POST['file_number'])
            print("file number", file_type_number)
            students = process_file(upfile.uploadedFile.name, file_type_number)

            if 'email_domain_name' in request.POST:
                email_domain = request.POST['email_domain_name']
                #this strips out leading at sign,because its predicted someone somewhere will enter @email domain
                email_domain = email_domain.replace('^@', '')

            if file_type_number == 0:
                for student_data in students:
                    username = student_data[3] + "@" + email_domain# The sutdnt username without @email domain
                    email = student_data[3] + "@" + email_domain
                    password = generate_secure_password()  # The SIS User ID found in the canvas csv file
                    generate_student_data(username, email, password, student_data, currentCourse, ccparams, file_type_number)
                    print("psswd", password)

            if file_type_number == 1:
                for student_data in students:
                    username = student_data[2] + "@" + email_domain# The sutdnt username without @email domain
                    email = student_data[2] + "@" +email_domain
                    password = generate_secure_password()
                    print("psswd", username, email, password, student_data, currentCourse, ccparams)
                    generate_student_data(username, email, str(password), student_data, currentCourse, ccparams, file_type_number)
                    

    return redirect('createStudentListView')
            
            
