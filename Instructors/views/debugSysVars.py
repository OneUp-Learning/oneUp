'''
Created on Sept 4, 2018

@author: joelevans
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Activities, ActivitiesCategory, Questions, Topics
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

from django.http import JsonResponse
    
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
        
        
        #Refines data from drop down menus and gets data needed to loop through to make the table
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
                objectType, objectTypeNames= getObjsForSysVarLocal(currentVar)
            

            if 'objectType' in request.POST:
                object = request.POST['objectType']
                if object == "all":
                    objectTypeDeBugTable = getObjsForSysVarLocal(currentVar)[0]
                    print(objectTypeDeBugTable)
                    context_dict['isAll'] = True
                else:
                    print("OBJECT:" + str(object))
                    currentObject = ObjectTypes.objectTypes[int(object)]
                    objectTypeDeBugTable.append(object)
                    context_dict['currentObj'] = int(object)
                
            
        #Get all the events for each student for each event in each object
        displayData = []
        for studentID in userIdDebugTable:
            for var in sysVarDeBugTable:
                for obj in objectTypeDeBugTable:
                    if type(var) == dict:
                        varIndex = var['index']
                    else:
                        varIndex = var
                    
                    print("########")
                    print(obj)
                    
                    displayData.extend(getSysValues(studentID,varIndex,obj,currentCourse))
        
        context_dict['debugData'] = displayData
                    
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
    

def getObjsForSysVarLocal(sysVar):
    objectTypes = ObjectTypes.objectTypes #enum of system objects
    objIndex =  list(sysVar['functions'].keys())
    objNames = []

    for i in objIndex:
        currentObj = objectTypes[i]
        objNames.append(currentObj)

    return objIndex, objNames

@login_required
def getObjsForSysVar(request):
    objectTypes = ObjectTypes.objectTypes #enum of system objects
    sysVars = SystemVariable.systemVariables #enums of system vars
    objects = {}

    if request.POST:
        sysVarIndex = request.POST['sysVarIndex']
        var = sysVars[int(sysVarIndex)]
        objIndex =  list(var['functions'].keys())
        objNames = []

        for i in objIndex:
            currentObj = objectTypes[i]
            objects[i] = currentObj
        
    return JsonResponse(objects)

def getSysValues(student,sysVar,objectType,currentCourse):
    values = []
    disaplyData = []

    objString = ObjectTypes.objectTypes[int(objectType)]

    #Get the objects from the db
    if objString == 'challenge':
        chall = Challenges.objects.filter(courseID=currentCourse).values('pk', 'challengeName')
        for x in chall:
            val = calculate_system_variable(sysVar,currentCourse,student,int(objectType),x['pk'])
            disaplyData.append(prepForDisplay(student,sysVar,objectType,val,x['challengeName']))

    elif objString == 'activity':
        acts = Activities.objects.filter(courseID=currentCourse).values('pk', 'activityName')
        for x in acts:
            val = calculate_system_variable(sysVar,currentCourse,student,int(objectType),x['pk'])
            disaplyData.append(prepForDisplay(student,sysVar,objectType,val,x['activityName']))
    
    elif objString == 'activityCategory':
        actCats = ActivitiesCategory.objects.filter(courseID=currentCourse).values('pk', 'name')
        for x in actCats:
           val = calculate_system_variable(sysVar,currentCourse,student,int(objectType),x['pk'])
           disaplyData.append(prepForDisplay(student,sysVar,objectType,val,x['name']))

    # elif objString == 'question':
    #     print('###########  question')
    #     #questions = Questions.objects.filter()
    #     #ASK ABOUT HOW TO GET QUESTON FROM THE COURSE

    # elif objString == 'topic':
    #     print('###########  topic')
    #     #ASK ABOUT HOW TO GET A TOPIC 

    elif objString == 'global':
        val = calculate_system_variable(sysVar,currentCourse,student,int(objectType),0)
        disaplyData.append(prepForDisplay(student,sysVar,objectType,val,0))

    return disaplyData

def prepForDisplay(student, sysVar, object, value,assignment):
    name = student.user.first_name + " " + student.user.last_name
    avatarImage = checkIfAvatarExist(StudentRegisteredCourses.objects.get(studentID=student))
    objectName = ObjectTypes.objectTypes[int(object)]
    sysVarName = SystemVariable.systemVariables[int(sysVar)]['name']
    if objectName == 'global':
        assignment = "N/A"
    if type(value) == str and "Error" in value:
        value = "No value available "
    return (name, assignment, objectName, sysVarName, value, avatarImage)