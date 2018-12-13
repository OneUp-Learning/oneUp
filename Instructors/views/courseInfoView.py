'''
Created on March 16, 2016


'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck   
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def courseInformation(request):

    context_dict, currentCourse = initialContextDict(request)
                 
    if request.method == 'POST':
        currentCourse.courseDescription = str(request.POST.get('courseDescr'))  
        currentCourse.save()     
        return redirect('instructorCourseHome.html')
    
    if request.method == 'GET':        
        context_dict['course_Description'] = currentCourse.courseDescription
        return render(request,'Instructors/CourseInformation.html', context_dict)


