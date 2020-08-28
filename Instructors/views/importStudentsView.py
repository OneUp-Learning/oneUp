'''
Created on April 12, 2017

@author: Christo Dichev
'''

from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse

from Instructors.views.utils import initialContextDict
from Instructors.models import UploadedFiles
from Instructors.constants import anonymous_avatar
from Instructors.views.preferencesView import createSCVforInstructorGrant
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck  
import json

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
                lines.append((values[0].strip(),values[1].strip(), values[2].strip()))

    print("line",lines)
    return lines


def generate_student_data(user_info, new_password, currentCourse, ccparams):
    # Check if student is in the system already
    new_student = user_info['new']
    
    if not new_student:
        users_list = User.objects.filter(username = user_info['username'])

        #the student is in the system, get it
        user = users_list[0] 
        student = Student.objects.get(user = user)              
                
    else:
        # the student is not in the system, create a user/student  

        # Check if the default generated password was changed
        password = None     
        if user_info['password'] !=  new_password and new_password.strip() != "":
            password = new_password
        else:
            password = user_info['password']

        user = User.objects.create_user(user_info['username'], user_info['email'], password)
        user.first_name = user_info['first-name']
        
        user.last_name = user_info['last-name']
        user.save()
        
        student = Student()
        student.user = user
        student.universityID = user_info['email']
        student.save()
    
    # register the student for this course
    if not StudentRegisteredCourses.objects.filter(courseID=currentCourse,studentID=student): # keeps us from registering the same students over and over
        studentRegisteredCourses = StudentRegisteredCourses()
        studentRegisteredCourses.studentID = student
        studentRegisteredCourses.courseID = currentCourse
        studentRegisteredCourses.avatarImage = anonymous_avatar
        if ccparams.virtualCurrencyAdded:
            # We have now switched to the canonical virtual currency amount a student has being determined by their transactions,
            # so we first add a StudentVirtualCurrency entry to show their gain and then we adjust the virtualCurrencyAmount.
            createSCVforInstructorGrant(student,currentCourse,ccparams.virtualCurrencyAdded)
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

    json_response = {'users': []}

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
                email_domain = email_domain.replace('@', '')

            if file_type_number == 0:
                index = -1
                for student_data in students:
                    username = student_data[3] + "@" + email_domain# The sutdnt username without @email domain
                    email = student_data[3] + "@" + email_domain
                    password = generate_secure_password()  # The SIS User ID found in the canvas csv file

                    # Return student info to frontend to show generated password
                    user_info = {'id': index, 'first-name': student_data[0][1:-1], 'last-name': student_data[1], 'username': username, 'email': email, 'password': password, 'new': True}
                    if User.objects.filter(username = username).exists():
                        user_info['new'] = False
                        user_info['id'] = User.objects.get(username = username).pk
                    else:
                        index -= 1
                        
                    json_response['users'].append(user_info)

                    print("psswd", password)

            if file_type_number == 1:
                index = -1
                for student_data in students:
                    username = student_data[2] + "@" + email_domain# The sutdnt username without @email domain
                    email = student_data[2] + "@" +email_domain
                    password = generate_secure_password()
                    print("psswd", username, email, password, student_data, currentCourse, ccparams)

                    # Return student info to frontend to show generated password
                    user_info = {'id': index, 'first-name': student_data[0], 'last-name': student_data[1], 'username': username, 'email': email, 'password': password, 'new': True}
                    if User.objects.filter(username = username).exists():
                        user_info['new'] = False
                        user_info['id'] = User.objects.get(username = username).pk
                    else:
                        index -= 1

                    json_response['users'].append(user_info)

            json_response['users'] = sorted(json_response['users'], key=lambda x: x['username'])
                    
    return JsonResponse(json_response)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def saveImportStudentsPasswords(request):

    context_dict, currentCourse = initialContextDict(request)
    ccparams = context_dict['ccparams']

    json_response = {'success': True}

    if request.method == 'POST':     
        # Create new users with the generated or new passwords
        if "users" in request.POST:
            users = json.loads(request.POST['users'])
            print(users)
            for user_info in users:
                if user_info['new']:
                    generate_student_data(user_info, request.POST["default-input-{}".format(user_info['id'])], currentCourse, ccparams)
                else:
                    generate_student_data(user_info, user_info['password'], currentCourse, ccparams)
                    
    return JsonResponse(json_response)
            
            
