'''
Created on jan 1, 2022

'''
import copy
import json
import logging


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
import js2py

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
        tempIntipic ='''var face = new Image();     
                        var nose = new Image();
                        var mouth = new Image();     
                        var eye = new Image();
                        var eyebrow = new Image();
                        var eyewear = new Image();     
                        var hair = new Image();  
                        var hairb = new Image();       
                        var fachair = new Image();
                        var clothes = new Image();  
                        var background = new Image();
                        
                     '''
    #    intipic = js2py.eval_js(tempIntipic)
        
        if request.method == "POST":
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
           st_ava.save()
           
        
       
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