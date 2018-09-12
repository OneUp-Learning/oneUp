from Instructors.views.utils import initialContextDict
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from django.contrib.auth.models import User
import glob

def studentInitialContextDict(request):    
    context_dict, currentCourse = initialContextDict(request)
    
    #student = Student.objects.get(user=request.user) 
    if 'userID' in request.GET:    
        stud = User.objects.get(username=request.GET['userID'])
        student = Student.objects.get(user=stud)
        context_dict["is_teacher"] = True
        context_dict['is_test_student'] = student.isTestStudent
    else:
        context_dict["is_student"] = True
        student = Student.objects.get(user=request.user)
        context_dict['is_test_student'] = student.isTestStudent
      
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
    context_dict['student'] = student
    print('context_dict')
    print(context_dict['student'])
    
    context_dict['avatar'] = checkIfAvatarExist(st_crs)
    
    if not currentCourse:
        context_dict['course_notselected'] = 'Please select a course'
        
        
    ##GGM determine if student has leaderboard enabled
    studentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=context_dict['student'])
    context_dict['studentLeaderboardToggle'] = studentConfigParams.displayLeaderBoard
    context_dict['displayClassSkills'] = studentConfigParams.displayClassSkills

        
    return context_dict,currentCourse

def studentInstructorInitialContextDict(request):
    
    context_dict, currentCourse = initialContextDict(request)
               
    if 'userID' in request.GET:    
        stud = User.objects.filter(username=request.GET['userID'])
        context_dict["is_teacher"] = True
    else:
        context_dict["is_student"] = True
        stud = request.user

    studentId = Student.objects.filter(user=stud)
    
def checkIfAvatarExist(student):
    avatars = glob.glob('static/images/avatars/*')
    defaultAvatar = '/static/images/avatars/anonymous.png'
    studentAvatarPath = student.avatarImage
    studentAvatarPath = studentAvatarPath[1:]
    if studentAvatarPath in avatars:
        return student.avatarImage
    else:
        student.avatarImage = defaultAvatar #change the students avatar to the default
        student.save()
    
    return defaultAvatar 

