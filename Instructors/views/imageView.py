'''
Created on Feb 24, 2017

@author: dichevad
'''
import os

from django.shortcuts import render, redirect

from Instructors.models import Courses, UploadedImages 
from django.conf.global_settings import MEDIA_URL


def imageUpload(request):
    context_dict = {}
    
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"] = request.user.username
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    if request.POST:        
        imageFile = request.FILES['imagefile']
        imageFileName = imageFile.name
        
        imageObject = UploadedImages() 
        imageObject.imageFile = imageFile
        imageObject.imageFileName = imageFileName
        imageObject.imageDescription = request.POST['description']
        imageObject.imageCreator = request.user
        imageObject.save()
        
    return redirect('/oneUp/instructors/imageList', context_dict)
    
def imageDelete(request):
    context_dict = {}
    
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"] = request.user.username
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    if request.POST: 
        if 'imageID' in request.POST:
            image = UploadedImages.objects.get(pk=int(request.POST['imageID']))
            image.delete()
        
    return redirect('/oneUp/instructors/imageList', context_dict)
    
       
def imageList(request):
 
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
        imageFilePath = []
        imageDescription = []                

    images = UploadedImages.objects.filter(imageCreator=request.user)

    for im in images: 
        path = os.path.join('../../media/images/uploadedInstructorImages/', im.imageFileName)          
        image.append(path)
        imageID.append(im.imageID)
        imageFilePath.append('/media/images/uploadedInstructorImages/' + im.imageFileName)
        imageDescription.append(im.imageDescription)
        
    context_dict['image_range'] = zip(range(1,images.count()+1),image,imageID,imageFilePath,imageDescription)
            
    return render(request,'Instructors/ImageList.html', context_dict)

