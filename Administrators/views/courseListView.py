

from django.template import RequestContext
from django.shortcuts import render, redirect

from Instructors.models import Courses

from django.contrib.auth.decorators import login_required

@login_required
def courseListView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context_dict = { }
        
    course_ID = []      
    course_Name = []
    #course_Author = []         
           
    crs = Courses.objects.all()
    for item in crs:
        course_ID.append(item.courseID) #pk
        course_Name.append(item.courseName)
        #course_Author.append(item.courseAuthor)
                    
    context_dict['course_range'] = zip(range(1,crs.count()+1),course_ID,course_Name)

    user = request.user    
    if user.groups.filter(name='Teachers').exists():
        context_dict["is_teacher"] = True
        return redirect('instructorHome')
    elif user.groups.filter(name='Admins').exists():
        context_dict["is_admin"] = True
        return redirect('adminHomeView')
    else:
        context_dict["is_student"] = True
        return redirect('StudentHome')
