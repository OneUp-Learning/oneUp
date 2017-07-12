'''
Created on Nov 14, 2016

@author: Joel Evans
'''

from django.shortcuts import render, redirect
import glob, os

from Instructors.models import TemplateDynamicQuestions, Challenges,ChallengesQuestions, Courses, TemplateTextParts, LuaLibrary, DependentLibrary ,\
    QuestionLibrary
from Instructors.lupaQuestion import lupa_available 

from Instructors.views import utils

from Badges.enums import QuestionTypes

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import sys
import re
from difflib import context_diff
from django.template.context_processors import request
from django.template.library import Library

@login_required
def luaLibUpload(request):
    context_dict,currentCourse = utils.initialContextDict(request)

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
        
        library.libraryName = library.libraryName.replace(" ","") 
            
        #Get the rest of info for the libary 
        library.libFile = request.FILES['libfile'] 
        library.libCreator = request.user
        
        #save object
        library.save() 
    
        #Get all the libs from the post and make dependencies 
        listOfDepends = request.POST.getlist('dependentLuaLibraries[]')
        
        #Link them with library to make dependent relationship    
        makeDependencies(library, listOfDepends)
    
    #List all of the libs we have
    libList(context_dict, request.user)
    
    return render(request, 'Instructors/uploadLuaLibs.html', context_dict)

@login_required
def libDelete(request):
    context_dict,currentCourse = utils.initialContextDict(request)
        
    if request.POST: 
        if 'libID' in request.POST:
            ID = int(request.POST['libID'])
            
            # Note: after these steps, we should consider adding some sort of missing dependency flag to libraries or questions
            # whose dependencies have been removed.
            
            DependentLibrary.objects.filter(mainLibrary=ID).delete() #delete the information about which libraries depend on it
            DependentLibrary.objects.filter(dependent=ID).delete() #delete the information about which libraries it depends on
            QuestionLibrary.objects.filter(library=ID).delete() #delete the problem dependencies
            currentLib = LuaLibrary.objects.get(pk=ID)
            currentLib.delete()
        
    return redirect('/oneUp/instructors/luaLibUploadView')

def libList(context_dict, user):
      
    #Get all Libraries 
    libs = LuaLibrary.objects.all()

    libList = []

    for lib in libs: 
        libDict = {}
        libDict['name'] = lib.libraryName
        libDict['description'] = lib.libDescription
        libDict['ID']= lib.libID
        libDict['myLib'] = lib.libCreator == user
        libDict['hasDependents'] = DependentLibrary.objects.filter(mainLibrary=lib).exists() or QuestionLibrary.objects.filter(library=lib).exists()
        libList.append(libDict)
                
    context_dict['lib_range'] = libList
    context_dict['luaLibraries'] = [lib.libraryName for lib in libs]
            
    return context_dict

def makeDependencies(library,listOfDependNames):
    existingDeps = DependentLibrary.objects.filter(dependent=library)
    existingDepNames = [dep.dependent.libraryName for dep in existingDeps]
    existingWithoutNew = [val for val in existingDepNames if val not in listOfDependNames]
    newWithoutExisting = [val for val in listOfDependNames if val not in existingDepNames]

    for name in newWithoutExisting:
        dependent = LuaLibrary.objects.get(libraryName= name)
        depend = DependentLibrary()
        depend.mainLibrary = library
        depend.dependent = dependent
        depend.save()
    for name in existingWithoutNew:
        DependentLibrary.objects.filter(mainLibrary=name,dependent__libraryName=library).delete()
        
def getDependencyLibraryNames(library):
    names = []
    depLibraries = DependentLibrary.objects.filter(dependent=library)
    for depLib in depLibraries:
        names.append(depLib.dependent.libraryName)
    return names

@login_required
def libEdit(request):
    context_dict,currentCourse = utils.initialContextDict(request)
        
    libList(context_dict, request.user)
        
    if request.POST: 
        #If the lib exist get it else make a new one 
        if 'libID' in request.POST:
            library = LuaLibrary.objects.get(pk=int(request.POST['libID']))
            context_dict['libEdit'] = True
            context_dict['libName'] = library.libraryName
            context_dict['libDescription'] = library.libDescription
            context_dict['libID'] = library.libID
            context_dict['selectedLuaLibraries'] = getDependencyLibraryNames(library)
            print(request.POST['libID'])
            
            
    return render(request, 'Instructors/uploadLuaLibs.html', context_dict)

@login_required
def libDeleteConfirmView(request):
    context_dict,currentCourse = utils.initialContextDict(request)
    
    libraryForDeletion = request.POST['libID']
    context_dict['libID'] = libraryForDeletion
    
    context_dict['libName'] = LuaLibrary.objects.get(pk=libraryForDeletion).libraryName

    dependentLibraries = DependentLibrary.objects.filter(mainLibrary=libraryForDeletion)
    dependentProblems = QuestionLibrary.objects.filter(library=libraryForDeletion)
    
    context_dict['libraryDependencyCount'] = dependentLibraries.count()
    context_dict['dependentLibraries'] = [depLib.dependent.libraryName for depLib in dependentLibraries]
    context_dict['problemDependencyCount'] = dependentProblems.count()
    context_dict['dependentProblems'] = [depProb.question.preview for depProb in dependentProblems]

    return render(request, 'Instructors/LibraryDeleteConfirmation.html', context_dict)