
from django.template import RequestContext
from django.shortcuts import render, redirect
from Instructors.models import Instructors, InstructorRegisteredCourses, Courses
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import adminsCheck

@login_required
@user_passes_test(adminsCheck,login_url='/oneUp/home',redirect_field_name='')
def deleteItemView(request):
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
    context_dict["username"]=user.username
    
    if 'courseToDelete' in request.POST:
        # Delete periodic tasks related to this course
        PeriodicTask.objects.filter(kwargs__contains='"course_id": '+request.POST["courseToDelete"]).delete()
        course = Courses.objects.get(pk=int(request.POST['courseToDelete']))
        #delete the unspeciefied topics for the course        
        course.delete()
    
    if 'instructorToDelete' in request.POST:
        instructor = User.objects.get(username=request.POST['instructorToDelete'])
        print("Deleted:", instructor)            
        instructor.delete()
    
    return redirect('/oneUp/administrators/adminHome.html')
            