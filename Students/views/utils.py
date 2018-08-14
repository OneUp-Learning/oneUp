from Instructors.views.utils import initialContextDict
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from django.contrib.auth.models import User

def studentInitialContextDict(request):
    context_dict, currentCourse = initialContextDict(request)
    
    #student = Student.objects.get(user=request.user) 
    if 'userID' in request.GET:    
        stud = User.objects.get(username=request.GET['userID'])
        student = Student.objects.get(user=stud)
        context_dict["is_teacher"] = True
    else:
        context_dict["is_student"] = True
        student = Student.objects.get(user=request.user)
      
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
    context_dict['student'] = student
    print('context_dict')
    print(context_dict['student'])
    context_dict['avatar'] = st_crs.avatarImage
    if not currentCourse:
        context_dict['course_notselected'] = 'Please select a course'
        
        
    ##GGM determine if student has leaderboard enabled
    context_dict['studentConfigParams'] = StudentConfigParams.objects.get(courseID=currentCourse, studentID=context_dict['student'])

        
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

