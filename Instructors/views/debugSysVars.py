'''
Created on Sept 4, 2018

@author: joelevans
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Activities, ActivitiesCategory
from Instructors.views.utils import initialContextDict, utcDate
from Instructors.constants import default_time_str
from Instructors.views.instructorCourseHomeView import studentXP
from Students.models import StudentRegisteredCourses, StudentChallenges, StudentActivities, StudentEventLog, Student
from Badges.enums import Event, ObjectTypes
from Badges.systemVariables import SystemVariable, calculate_system_variable
from Students.views.avatarView import checkIfAvatarExist
from termios import CRPRNT
from lib2to3.fixes.fix_input import context
from django.contrib.auth.models import User

import collections
    
@login_required
def debugSysVars(request):
    
    context_dict, currentCourse = initialContextDict(request)
    defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
    
    #Student info
    courseStudents = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    userID, first_Name, last_Name, user_Avatar = getAllStudents(courseStudents)

    #Object Types for the course
    objectType = ObjectTypes.objectTypes #enum of system objects
    objectTypeNames = []
        
    #System variables 
    sysVars = SystemVariable.systemVariables #enum of system vars
    sysVarsName = []
    
    
    for var in sysVars:
        print(sysVars[var]["name"])
        sysVarsName.append(sysVars[var]["name"])
        
    for o in objectType:
        objectTypeNames.append(objectType[o])
    
    #Used to populate the table with debugged information
    if request.POST:
        #Studnt info
        userIdDebugTable = []
        first_NameDebugTable = []
        last_NameDebugTable = []
        user_AvatarDebugTable = []
        
        #Event info
        sysVarDeBugTable = []
        sysVarNamesDebugTable = []
        allDebugEvents = []
        
        #Object info
        objectTypeDeBugTable = []
        objectNamesDebugTable = []
        
        
        
        if 'student' in request.POST:
            student = request.POST['student']
            if student == "all":
                userIdDebugTable, first_NameDebugTable, last_NameDebugTable, user_AvatarDebugTable = getAllStudents(courseStudents)
            else:
               user = User.objects.get(username=student)
               cs = Student.objects.get(user=user)
               currentStudent =  StudentRegisteredCourses.objects.get(courseID=currentCourse,studentID=cs)
               userIdDebugTable.append(currentStudent.studentID)
               context_dict['currentStudet'] = currentStudent.studentID
                    
        if 'sysVar' in request.POST:
            sysVarIndex = request.POST['sysVar']
            if sysVarIndex == "all" :
                sysVarDeBugTable = sysVars 
                sysVarNamesDebugTable = sysVarsName
            else:
                currentVar = sysVars[int(sysVarIndex)]
                sysVarDeBugTable.append(currentVar)
                sysVarNamesDebugTable.append(currentVar['name'])
                context_dict['currenSysVar'] = int(sysVarIndex)
                print(currentVar)
                objectType, objectTypeNames= getObjsForSysVar(currentVar)
            

            if 'objectType' in request.POST:
                object = request.POST['objectType']
                if object == "all":
                    objectTypeDeBugTable = ObjectTypes.objectTypes
                else:
                    print("OBJECT:" + str(object))
                    currentObject = ObjectTypes.objectTypes[int(object)]
                    objectTypeDeBugTable.append(object)
                    objectNamesDebugTable.append(currentObject)
                    context_dict['currentObj'] = int(object)
                
            
        #Get all the events for each student for each event in each object
        for studentID in userIdDebugTable:
            for var in sysVarDeBugTable:
                for obj in objectTypeDeBugTable:
                    if type(var) == dict:
                        varIndex = var['index']
                    else:
                        varIndex = var

                    val = calculate_system_variable(varIndex,currentCourse,studentID,obj,obj)
                    print(val)
                         
                    
                    
                    # allStudentEventsObj = StudentEventLog.objects.filter(student=studentID,course=currentCourse,event=eventIndex,objectType=obj).order_by('-timestamp')
                    # allDebugEvents.extend(allStudentEventsObj)
                        
        # #Order them for display
        # displayStudents = []
        # displayEvents = []
        # displayObject = []   
        # disaplyTimeStamp = []
        # for sEventLog in allDebugEvents:
        #     name = sEventLog.student.user.first_name + " " + sEventLog.student.user.last_name
        #     e = events[sEventLog.event]['name']
        #     o = objectType[sEventLog.objectType]
        #     timestamp = sEventLog.timestamp
        #     displayStudents.append(name)
        #     displayEvents.append(e)
        #     displayObject.append(o)
        #     disaplyTimeStamp.append(timestamp)
        
        
        
    # Used to fill values for the three drop down menus
    context_dict['user_range'] = sorted(list(zip(range(1,courseStudents.count()+1),userID,first_Name,last_Name,user_Avatar, )))
    context_dict['sysVars'] = sorted(list(zip(range(1,len(sysVars)+1), sysVars, sysVarsName, )))
    context_dict['objects'] = sorted(list(zip(range(1,len(objectType)+1), objectType, objectTypeNames, )))
    
        # context_dict['debugTable'] = list(zip(range(1,len(allDebugEvents)+1), displayStudents, displayEvents, displayObject, disaplyTimeStamp))


    return render(request,'Instructors/DebugSysVars.html', context_dict)

def getAllStudents(courseStudents):
    studentList = []
    userID = []
    first_Name = []
    last_Name = []
    user_Avatar = []
    
    for cs in courseStudents:
        s = cs.studentID
        userID.append(s)
        first_Name.append(s.user.first_name)
        last_Name.append(s.user.last_name)
        user_Avatar.append(checkIfAvatarExist(cs))
    
    return userID, first_Name, last_Name, user_Avatar
    

def getObjsForSysVar(sysVar):
    objectTypes = ObjectTypes.objectTypes #enum of system objects
    objIndex =  list(sysVar['functions'].keys())
    objNames = []

    for i in objIndex:
        currentObj = objectTypes[i]
        objNames.append(currentObj)
    
    return objIndex, objNames