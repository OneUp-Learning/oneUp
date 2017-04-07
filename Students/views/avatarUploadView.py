'''
Created on Feb 1, 2017

@author: Joel Evans
'''

import os
from django.shortcuts import render, redirect

from Students.models import Courses, Student, UploadedAvatarImage, StudentRegisteredCourses 
from django.conf.global_settings import MEDIA_URL


def avatarUpload(request):
    context_dict = {}
    
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"] = request.user.username
        
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    if request.POST:        
        avatarImage = request.FILES['myfile']
        avatarImageFileName = avatarImage.name
        print(avatarImageFileName)
        print(MEDIA_URL)
        
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

       

