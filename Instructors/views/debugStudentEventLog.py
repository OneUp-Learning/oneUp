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
from Students.views.avatarView import checkIfAvatarExist
from termios import CRPRNT
from lib2to3.fixes.fix_input import context
from django.contrib.auth.models import User

import collections
    
@login_required
def debugEventVars(request):
    
    context_dict, currentCourse = initialContextDict(request)
    defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
    
    #Student info
    courseStudents = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
    userID, first_Name, last_Name, user_Avatar = getAllStudents(courseStudents)



    #Object Types for the course
    courseChallenges = Challenges.objects.filter(courseID=currentCourse)
    courseActivities = Activities.objects.filter(courseID=currentCourse)
    courseWarmupChallenges = Challenges.objects.filter(courseID=currentCourse)
    courseActivitiesCats = ActivitiesCategory.objects.filter(courseID=currentCourse)
    #Ask about topics sicne they are not connect to a course
    #Ask about questions and what we should filter by since not connect to a course
    #Ask about how to show forms
    objectType = ObjectTypes.objectTypes
    objectTypeNames = []
        
    #Events we have in the systemq
    events = Event.events 
    eventNames = []
    
    
    for e in events:
        eventNames.append(events[e]["name"])
        
    for o in objectType:
        objectTypeNames.append(objectType[o])
    
    
    # Used to fill values for the three drop down menus
    context_dict['user_range'] = sorted(list(zip(range(1,courseStudents.count()+1),userID,first_Name,last_Name,user_Avatar, )))
    context_dict['events'] = sorted(list(zip(range(1,len(events)+1), events, eventNames, )))
    context_dict['objects'] = sorted(list(zip(range(1,len(objectType)+1), objectType, objectTypeNames, )))
    
    
    
    
    #Used to populate the table with debugged information
    if request.POST:
        #Studnt info
        userIdDebugTable = []
        first_NameDebugTable = []
        last_NameDebugTable = []
        user_AvatarDebugTable = []
        
        #Event info
        eventsDeBugTable = []
        eventNamesDebugTable = []
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
               first_NameDebugTable.append(currentStudent.studentID.user.first_name)
               last_NameDebugTable.append(currentStudent.studentID.user.last_name)
               user_AvatarDebugTable.append(checkIfAvatarExist(currentStudent))
               context_dict['currentStudet'] = currentStudent.studentID
        
               
            context_dict['debuggedStudent'] = sorted(list(zip(range(1,len(userIdDebugTable)+1),userIdDebugTable,first_NameDebugTable,last_NameDebugTable,user_AvatarDebugTable)))
            
        if 'events' in request.POST:
            event = request.POST['events']
            if event == "all" :
                eventsDeBugTable = events 
                eventNamesDebugTable = eventNames
            else:
                currentEvent = events[int(event)]
                eventsDeBugTable.append(currentEvent)
                eventNamesDebugTable.append(currentEvent['name'])
                context_dict['currentEvent'] = int(event)
                
            
            context_dict['debuggedEvents'] = sorted(list(zip(range(1, len(eventsDeBugTable)+1), eventsDeBugTable, eventNamesDebugTable)))
        
        if 'objectType' in request.POST:
            object = request.POST['objectType']
            if object == "all":
                objectTypeDeBugTable = ObjectTypes.objectTypes
            else:
                currentObject = objectType[int(object)]
                objectTypeDeBugTable.append(object)
                objectNamesDebugTable.append(currentObject)
                context_dict['currentObj'] = int(object)
                
            
        #Get all the events for each student for each event in each object
        for studentID in userIdDebugTable:
            for ourEvent in eventsDeBugTable:
                for obj in objectTypeDeBugTable:
                    if type(ourEvent) == dict:
                        eventIndex = ourEvent['index']
                    else:
                        eventIndex = ourEvent
                         
                    allStudentEventsObj = StudentEventLog.objects.filter(student=studentID,course=currentCourse,event=eventIndex,objectType=obj).order_by('-timestamp')
                    allDebugEvents.extend(allStudentEventsObj)
                        
        #Order them for display
        displayStudents = []
        displayEvents = []
        displayObject = []   
        disaplyTimeStamp = []
        for sEventLog in allDebugEvents:
            name = sEventLog.student.user.first_name + " " + sEventLog.student.user.last_name
            e = events[sEventLog.event]['name']
            o = objectType[sEventLog.objectType]
            timestamp = sEventLog.timestamp
            displayStudents.append(name)
            displayEvents.append(e)
            displayObject.append(o)
            disaplyTimeStamp.append(timestamp)
        
        
        context_dict['debugTable'] = list(zip(range(1,len(allDebugEvents)+1), displayStudents, displayEvents, displayObject, disaplyTimeStamp))

    return render(request,'Instructors/DebugStudentEventLog.html', context_dict)

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
    

def getAlllEvents():
    pass
