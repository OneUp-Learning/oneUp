'''
Created on Feb 24, 2017

@author: dichevad
'''
import os

from django.shortcuts import render, redirect

from Instructors.models import Courses, UploadedImages 
from Instructors.views.utils import initialContextDict
from django.conf.global_settings import MEDIA_URL
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck   

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def imageUpload(request):
    context_dict, currentCourse = initialContextDict(request)
        
    if request.POST and len(request.FILES) != 0:        
        imageFile = request.FILES['imagefile']
        imageFileName = os.path.basename(imageFile.name)
        
        imageObject = UploadedImages() 
        imageObject.imageFile = imageFile
        imageObject.imageFileName = imageFileName
        imageObject.imageDescription = request.POST['description']
        imageObject.imageCreator = request.user
        imageObject.save()
        
    return redirect('/oneUp/instructors/imageList', context_dict)
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')      
def imageDelete(request):
    context_dict, currentCourse = initialContextDict(request)
        
    if request.POST: 
        if 'imageID' in request.POST:
            image = UploadedImages.objects.get(pk=int(request.POST['imageID']))
            image.delete()
        
    return redirect('/oneUp/instructors/imageList', context_dict)
    
       
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def imageList(request):
 
    context_dict, currentCourse = initialContextDict(request)
      
    image = [] 
    imageID = []     
    imageFilePath = []
    imageDescription = []                

    images = UploadedImages.objects.filter(imageCreator=request.user)

    for im in images: 
        path = im.imageFile.url        
        image.append(path)
        imageID.append(im.imageID)
        imageFilePath.append(im.imageFile)
        imageDescription.append(im.imageDescription)
        
    context_dict['image_range'] = zip(range(1,images.count()+1),image,imageID,imageFilePath,imageDescription)
            
    return render(request,'Instructors/ImageList.html', context_dict)

