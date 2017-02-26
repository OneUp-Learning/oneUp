'''
Created on Feb 23, 2017

@author: dichevad
'''
import os

from django.shortcuts import render
from Instructors.models import  Courses, UploadedImages 
from django.contrib.auth.decorators import login_required

@login_required
def filesList(request):
 
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
          
        image = [] 
        imageID = []     
        imageFileName = []
        imageDescription = []                

    images = UploadedImages.objects.filter(imageCreator=request.user)
    print(str(images.count()))
    for im in images: 
        path = os.path.join('../../media/images/uploadedInstructorImages/', im.imageFileName)          
        image.append(path)
        imageID.append(im.imageID)
        imageFileName.append(im.imageFileName)
        imageDescription.append(im.imageDescription)
        
    context_dict['image_range'] = zip(range(1,images.count()+1),image,imageID,imageFileName,imageDescription)
            
    return render(request,'Instructors/FilesList.html', context_dict)
