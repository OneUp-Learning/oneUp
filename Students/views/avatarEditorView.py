'''
Created on jan 1, 2022

'''
import copy
import json
import logging
import os

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from notify.signals import notify

from Badges.enums import Action, Event, ObjectTypes, dict_dict_to_zipped_list
from Badges.events import register_event, recalculate_student_virtual_currency_total
from Badges.models import (ActionArguments, CourseConfigParams, RuleEvents,
                           VirtualCurrencyCustomRuleInfo,
                           VirtualCurrencyRuleInfo)
from Instructors.constants import unlimited_constant
from Instructors.models import InstructorRegisteredCourses
from Instructors.views.utils import current_localtime
from Students.models import StudentCustomAvatar
from Students.views.utils import studentInitialContextDict
from PIL import Image,ImageDraw

@login_required
def AvatarEditorView(request):
   
    
    context_dict, currentCourse = studentInitialContextDict(request)

    # Redirects students from VC page if VC not enabled
    config = CourseConfigParams.objects.get(courseID=currentCourse)
    if 'currentCourseID' in request.session:
        student = context_dict['student']
        st_ava_list = StudentCustomAvatar.objects.filter(studentID = student)
        if len(st_ava_list)==0:
            st_ava = StudentCustomAvatar()
            st_ava.studentID = student            
            st_ava.save()
        else:
            st_ava = st_ava_list[0]
    
        
       
        if request.method == "POST":
           name = student.__str__() +'_profilePicture.png'
           path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
           path1 = path + "/static/images/generatedAvatarImages/"
           path2 = path + "/static/images/customAvatarParts/"
           
           st_ava.faceIndex       = request.POST['iteSelect1']
           st_ava.noseIndex       = request.POST['iteSelect2']
           st_ava.mouthIndex      = request.POST['iteSelect3']
           st_ava.eyeIndex        = request.POST['iteSelect4']
           st_ava.eyebrowIndex    = request.POST['iteSelect5']
           st_ava.eyewearIndex    = request.POST['iteSelect6']
           st_ava.hairIndex       = request.POST['iteSelect7']
           st_ava.fahairIndex     = request.POST['iteSelect8']
           st_ava.clothesIndex    = request.POST['iteSelect9']
           st_ava.backgroundIndex = request.POST['iteSelect10']
           
           st_ava.faceColorIndex       = request.POST['colSelect1'] 
           st_ava.eyeColorIndex        = request.POST['colSelect2'] 
           st_ava.eyebrowColorIndex    = request.POST['colSelect3'] 
           st_ava.eyewearColorIndex    = request.POST['colSelect4']
           st_ava.hairColorIndex       = request.POST['colSelect5']
           st_ava.fahairColorIndex     = request.POST['colSelect6']  
           st_ava.clothesColorIndex    = request.POST['colSelect7'] 
           st_ava.backgroundColorIndex = request.POST['colSelect8']
           
           st_ava.image = "/static/images/generatedAvatarImages/" + name
           st_ava.save()
           
           
          # os.remove(path1+name)
           img = Image.new("RGBA", ( 384, 384))
           fac      = Image.open(path2 + "faces/col"      +str(st_ava.faceColorIndex)
                                 + "_face"       +str(st_ava.faceIndex)+".png" )           
           clothes  = Image.open(path2 + "clothes/col"    +str(st_ava.clothesColorIndex )
                                 + "_clothe"     +str(st_ava.clothesIndex) +".png" )        
           eyebrows = Image.open(path2 + "eyebrows/col"   +str(st_ava.eyebrowColorIndex)
                                 + "_eyebrows"   +str(st_ava.eyebrowIndex)+".png" )           
           eyes     = Image.open(path2 + "eyes/col"       +str(st_ava.eyeColorIndex)
                                 + "_eye"        +str(st_ava.eyeIndex)+".png" )
           if(int(st_ava.eyewearIndex) > 0):
               eyewear  = Image.open(path2 + "eyewear/col"    +str(st_ava.eyewearColorIndex)
                                 + "_eyewear"    +str(st_ava.eyewearIndex)+".png" )
           if(int(st_ava.fahairIndex) > 0):
               facHair  = Image.open(path2 + "facial_hair/col"+str(st_ava.fahairColorIndex) 
                                 + "_facialhair" +str(st_ava.fahairIndex)  +".png" )           
           hair1    = Image.open(path2 + "hair/col"       +str(st_ava.hairColorIndex)   
                                 + "_hair"       +str(st_ava.hairIndex)    +".png" )           
           hair2    = Image.open(path2 + "hair/col"       +str(st_ava.hairColorIndex)
                                 + "_hairb"      +str(st_ava.hairIndex)+".png" )           
           mouth    = Image.open(path2 + "mouths/col"     +str(st_ava.faceColorIndex)
                                 + "_mouth"      +str(st_ava.mouthIndex)+".png" )           
           nose     = Image.open(path2 + "noses/col"      +str(st_ava.faceColorIndex)
                                 + "_nose"       +str(st_ava.noseIndex)+".png" )
           background = Image.open(path2 + "backgrounds/col"      +str(st_ava.backgroundColorIndex)
                                 + "_background"       +str(st_ava.backgroundIndex)+".png" )
           box1 = (33, 64)
           box2 = (33, 19)
           img.paste(background, (0,0), mask=background)
           img.paste(     hair2,  box2, mask=hair2)          
           img.paste(       fac,  box1, mask=fac)        
           img.paste(      nose,  box2, mask=nose)          
           img.paste(     mouth,  box2, mask=mouth)         
           img.paste(      eyes,  box2, mask=eyes)           
           img.paste(  eyebrows,  box2, mask=eyebrows)  
           if(int(st_ava.eyewearIndex) > 0):       
               img.paste( eyewear, box2, mask=eyewear)     
           img.paste( clothes, box1, mask=clothes)
           img.paste(   hair1, box2, mask=hair1)  
           if(int(st_ava.fahairIndex) > 0):
               img.paste( facHair, box2, mask=facHair)
                 
          
           print(st_ava.image)           
           
           img.save( path1 + name)
            
        context_dict['faceSel']       = st_ava.faceIndex
        context_dict['noseSel']       = st_ava.noseIndex
        context_dict['mouthSel']      = st_ava.mouthIndex
        context_dict['eyeSel']        = st_ava.eyeIndex
        context_dict['eyebrowSel']    = st_ava.eyebrowIndex
        context_dict['eyewearSel']    = st_ava.eyewearIndex
        context_dict['hairSel']       = st_ava.hairIndex
        context_dict['facialSel']     = st_ava.fahairIndex
        context_dict['clothesSel']    = st_ava.clothesIndex
        context_dict['backgroundSel'] = st_ava.backgroundIndex
        
        context_dict['faceCol']       = st_ava.faceColorIndex
        context_dict['eyeCol']        = st_ava.eyeColorIndex
        context_dict['eyebrowCol']    = st_ava.eyebrowColorIndex
        context_dict['eyewearCol']    = st_ava.eyewearColorIndex
        context_dict['hairCol']       = st_ava.hairColorIndex
        context_dict['facialCol']     = st_ava.fahairColorIndex
        context_dict['clothesCol']    = st_ava.clothesColorIndex
        context_dict['backgroundCol'] = st_ava.backgroundColorIndex
            
    return render(request,'Students/AvatarEditor.html', context_dict   )