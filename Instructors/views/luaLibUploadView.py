'''
Created on Nov 14, 2016

@author: Joel Evans
'''

from django.shortcuts import render, redirect
import glob, os

from Instructors.models import TemplateDynamicQuestions, Challenges,ChallengesQuestions, Courses, TemplateTextParts, LuaLibrary, dependentLibrary 
from Instructors.lupaQuestion import lupa_available 

from Instructors.views import utils


from Badges.enums import QuestionTypes

from django.views.decorators.csrf import csrf_exempt
import sys
import re
from difflib import context_diff
from django.template.context_processors import request

def luaLibUpload(request):

    context_dict = {}
    
   # extractPaths(context_dict)
    #extractUploadedPaths(context_dict)
    
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"] = request.user.username       
        
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'

    string_attributes = ['libraryName','libDescription']

    if request.POST: 
        #If the lib exist get it else make a new one 
        if 'libID' in request.POST and request.POST['libID'] != '':
           print(request.POST['libID'])
           library = LuaLibrary.objects.get(pk=int(request.POST['libID'])) 
           library.removeFile()
           
        else:
            library = LuaLibrary()
                   
        #Copy all string from Post to database object
        for attr in string_attributes:
            setattr(library, attr, request.POST[attr])    
            
        #Get the rest of info for the libary 
        library.libFile = request.FILES['libfile'] 
        library.libCreator = request.user
        
        #save object
        library.save() 
    
        #Get all the libs from the post and make dependencies 
        listOfDepends = request.POST.getlist('dependentLuaLibraries[]')
        print(len(listOfDepends))
        
        #Link them with library to make dependent relationship    
        makeDependencies(library, listOfDepends)
    
    #List all of the libs we have
    libList(context_dict, request.user)
    
    
    
    return render(request, 'Instructors/uploadLuaLibs.html', context_dict)

def libDelete(request):
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
        if 'libID' in request.POST:
            ID = int(request.POST['libID'])
            dependentLibrary.objects.filter(mainLibary=ID).delete() #delete the dependencies  
            currentLib = LuaLibrary.objects.get(pk=ID)
            currentLib.delete()
        
    return redirect('Instructors/uploadLuaLibs.html')

def libList(context_dict, user):
      
    #Arrays to hold the lib names and lib description            
    libName = []
    libDescription = []  
    libIDs = []     
    myLibs= []    #This is used to hold booleans so we can know if the lib is the users or not     
    
    #Get all Libraries 
    libs = LuaLibrary.objects.all()

    for lib in libs: 
        libName.append(lib.libraryName)          
        libDescription.append(lib.libDescription)
        libIDs.append(lib.libID)
        if lib.libCreator == user:
            myLibs.append(True)
        else:    
            myLibs.append(False)
                
    context_dict['lib_range'] = list(zip(range(1,libs.count()+1),libName,libDescription,libIDs,myLibs))
    context_dict['luaLibraries'] = libName
            
    return context_dict

def makeDependencies(library,listOfDepends):
    for name in listOfDepends:
        dependent = LuaLibrary.objects.get(libraryName= name)
        depend = dependentLibrary()
        depend.mainLibrary = library
        depend.dependent = dependent
        depend.save()
        
def getDependentLibraryNames(library):
    names = []
    depLibraries = dependentLibrary.objects.filter(mainLibrary=library)
    for depLib in depLibraries:
        names.append(depLib.dependent.libraryName)
    return names
        
def libEdit(request):
    context_dict = {}
    
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"] = request.user.username
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    libList(context_dict, request.user)
        
    if request.POST: 
        #If the lib exist get it else make a new one 
        if 'libID' in request.POST:
            library = LuaLibrary.objects.get(pk=int(request.POST['libID']))
            context_dict['libEdit'] = True
            context_dict['libName'] = library.libraryName
            context_dict['libDescription'] = library.libDescription
            context_dict['libID'] = library.libID
            context_dict['selectedLuaLibraries'] = getDependentLibraryNames(library)
            print(request.POST['libID'])
            
            
    return render(request, 'Instructors/uploadLuaLibs.html', context_dict)

