'''
Created on Feb 1, 2017

@author: Joel Evans
'''

import os
from django.shortcuts import render, redirect

from Students.models import Student, UploadedAvatarImage, StudentRegisteredCourses 
from Students.views.utils import studentInitialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def avatarUpload(request):
    
    context_dict,currentCourse = studentInitialContextDict(request)
            
    if request.POST:        
        avatarImage = request.FILES['myfile']
        avatarImageFileName = avatarImage.name
        
        avatarImagePerson = UploadedAvatarImage() 
        avatarImagePerson.avatarImage = avatarImage
        avatarImagePerson.avatarImageFileName = avatarImageFileName
        avatarImagePerson.save()
        
        path = os.path.join('../../media/images/uploadedAvatarImages/', avatarImageFileName)
        
        student = Student.objects.get(user=request.user)       
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)     
        st_crs.avatarImage = path
        st_crs.save()
        
        context_dict['avatarImage'] = avatarImage
        context_dict['avatar'] = path
        
        return redirect('/oneUp/students/StudentCourseHome', context_dict)
    
    return render(request, 'Students/Avatar.html', context_dict)

       

