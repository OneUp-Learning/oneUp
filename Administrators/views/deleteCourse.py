
from django.template import RequestContext
from django.shortcuts import render, redirect
from Instructors.models import Courses
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def courseDeleteView(request):
    
        context_dict = { }
        context_dict["logged_in"]=request.user.is_authenticated()
        if request.user.is_authenticated():
            user = request.user
        context_dict["username"]=user.username
        
        # Retrieved all courses and append them to the context dict
        courses = Courses.objects.all()
        course_ID = []
        course_Name = []
        for c in courses:
            course_ID.append(c.courseID)
            course_Name.append(c.courseName)
        print(course_ID)
        
        context_dict['courses'] = zip(range(1, len(courses)+1), course_ID, course_Name)
        
        # If request is GET then return the context dict
        if request.method=='GET':
            return render(request,'Administrators/deleteCourse.html',context_dict)
        else: # Method is POST then delete selected course (AH)
            if request.POST['courseToDelete']:
                course = Courses.objects.get(pk=int(request.POST['courseToDelete']))            
                course.delete()
                
            return redirect('/oneUp/administrators/adminHome.html')
            