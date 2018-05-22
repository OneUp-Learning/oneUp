
from django.template import RequestContext
from django.shortcuts import render, redirect
from Instructors.models import Instructors, InstructorRegisteredCourses, Courses
from django.contrib.auth.models import User

def deleteItemView(request):
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        user = request.user
    context_dict["username"]=user.username
    
    if request.POST['courseToDelete']:
        course = Courses.objects.get(pk=int(request.POST['courseToDelete']))            
        course.delete()
    
    if request.POST['instructorToDelete']:
        instructor = User.objects.get(username=request.POST['instructorToDelete'])
        print("Deleted:", instructor)            
        instructor.delete()
    
    return redirect('/oneUp/administrators/adminHome.html')
            