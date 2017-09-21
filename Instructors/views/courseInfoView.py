'''
Created on March 16, 2016


'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Courses
from django.contrib.auth.decorators import login_required

@login_required

def courseInformation(request):

    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'  
                 
    if request.POST:
        if 'currentCourseID' in request.session:
            currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
            currentCourse.courseDescription = str(request.POST.get('courseDescr'))  
            currentCourse.save()     
        return render(request,'Instructors/InstructorCourseHome.html', context_dict)

    else:
        # GET request
        if 'currentCourseID' in request.session:
            currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))        
            context_dict['course_Description'] = currentCourse.courseDescription
            print(str(context_dict))
        return render(request,'Instructors/CourseInformation.html', context_dict)


