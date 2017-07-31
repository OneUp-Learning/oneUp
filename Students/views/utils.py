from Instructors.views.utils import initialContextDict
from Students.models import Student, StudentRegisteredCourses

def studentInitialContextDict(request):
    context_dict, currentCourse = initialContextDict(request)
    student = Student.objects.get(user=request.user)   
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
    context_dict['avatar'] = st_crs.avatarImage
    if not currentCourse:
        context_dict['course_notselected'] = 'Please select a course'
    return context_dict,currentCourse