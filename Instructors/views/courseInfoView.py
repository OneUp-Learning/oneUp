'''
Created on March 16, 2016


'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Instructors.views.utils import initialContextDict
@login_required

def courseInformation(request):

    context_dict, currentCourse = initialContextDict(request)
                 
    if request.method == 'POST':
        currentCourse.courseDescription = str(request.POST.get('courseDescr'))  
        currentCourse.save()     
        return redirect('instructorCourseHome.html')
    
    if request.method == 'GET':        
        context_dict['course_Description'] = currentCourse.courseDescription
        return render(request,'Instructors/CourseInformation.html', context_dict)


