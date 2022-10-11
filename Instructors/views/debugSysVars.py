'''
Created on Sept 4, 2018

@author: joelevans
'''


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

from Badges.enums import Event, ObjectTypes
from Badges.periodicVariables import (
    PeriodicVariables, TimePeriods, get_periodic_variable_results_for_student)
from Badges.systemVariables import SystemVariable, calculate_system_variable
from Instructors.constants import (uncategorized_activity,
                                   unspecified_topic_name)
from Instructors.models import (Activities, ActivitiesCategory, Challenges,
                                CoursesTopics, Questions,UniversityCourses)
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Students.models import (Student, StudentActivities, StudentChallenges,
                             StudentEventLog, StudentRegisteredCourses)
from Students.views.avatarView import checkIfAvatarExist


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def debugSysVars(request):

    context_dict, currentCourse = initialContextDict(request)

    # Student info
    courseStudents = StudentRegisteredCourses.objects.filter(
        courseID=currentCourse)
    userID, first_Name, last_Name, user_Avatar = getAllStudents(courseStudents)

    # Object Types for the course
    objectType = ObjectTypes.objectTypes  # enum of system objects
    objectTypeNames = []

    for o in objectType:
        objectTypeNames.append(objectType[o])

    # Used to populate the table with debugged information
    if request.POST:
        # Studnt info
        userIdDebugTable = []
        first_NameDebugTable = []
        last_NameDebugTable = []
        user_AvatarDebugTable = []

        # Event info
        sysVarDeBugTable = []
        allDebugEvents = []

        # Object info
        objectTypeDeBugTable = []

        # Refines data from drop down menus and gets data needed to loop through to make the table
        if 'student' in request.POST:
            student = request.POST['student']
            if student == "all":
                userIdDebugTable, first_NameDebugTable, last_NameDebugTable, user_AvatarDebugTable = getAllStudents(
                    courseStudents)
            else:
                user = User.objects.get(username=student)
                cs = Student.objects.get(user=user)
                currentStudent = StudentRegisteredCourses.objects.get(
                    courseID=currentCourse, studentID=cs)
                userIdDebugTable.append(currentStudent.studentID)
                context_dict['currentStudet'] = currentStudent.studentID

        current_time_period = None
        if 'sysVar' in request.POST:
            var_index = int(request.POST['sysVar'])
            context_dict['currenSysVar'] = int(var_index)
            if var_index in SystemVariable.systemVariables:
                currentVar = SystemVariable.systemVariables[var_index]
                sysVarDeBugTable.append(currentVar)
                
                objectType, objectTypeNames = getObjsForSysVarLocal(currentVar)
            else:
                currentVar = PeriodicVariables.periodicVariables[var_index]
                sysVarDeBugTable.append(currentVar)
                objectType, objectTypeNames = get_object_type_for_periodic_var(currentVar)
                context_dict['periodic_var_selected'] = True

            if 'time_period' in request.POST:
                context_dict['current_tp'] = int(request.POST['time_period'])
                current_time_period = context_dict['current_tp']

            if 'objectType' in request.POST:
                object_id = request.POST['objectType']
                if object_id == "all":
                    if var_index in SystemVariable.systemVariables:
                        objectTypeDeBugTable = getObjsForSysVarLocal(currentVar)[0]
                    else:
                        objectTypeDeBugTable = get_object_type_for_periodic_var(currentVar)[0]

                    # print(objectTypeDeBugTable)
                    context_dict['isAll'] = True
                else:
                    print("OBJECT:" + str(object_id))
                    currentObject = ObjectTypes.objectTypes[int(object_id)]
                    objectTypeDeBugTable.append(object_id)
                    context_dict['currentObj'] = int(object_id)

        # Get all the events for each student for each event in each object
        displayData = []
        for studentID in userIdDebugTable:
            for var in sysVarDeBugTable:
                for obj in objectTypeDeBugTable:
                    if type(var) == dict:
                        varIndex = var['index']
                    else:
                        varIndex = var

                    displayData.extend(getSysValues(
                        studentID, varIndex, obj, currentCourse, current_time_period))

        context_dict['debugData'] = displayData

    # Used to fill values for the three drop down menus
    context_dict['user_range'] = sorted(list(zip(range(1, courseStudents.count()+1), userID, first_Name, last_Name, user_Avatar, )), key=lambda x: (x[2].casefold(), x[3].casefold()))

    context_dict['system_variables'] = sorted([ x for i, x in SystemVariable.systemVariables.items()], key=lambda x: x['displayName'])
    
    exclude_periodic_variables = [PeriodicVariables.challenge_streak, PeriodicVariables.attendance_streak, 
            PeriodicVariables.warmup_challenge_greater_or_equal_to_40, PeriodicVariables.warmup_challenge_greater_or_equal_to_80]
    context_dict['periodic_variables'] = sorted([ x for i, x in PeriodicVariables.periodicVariables.items() if i not in exclude_periodic_variables ], key=lambda x: x['displayName'])

    context_dict['time_periods'] = [x for i,x in TimePeriods.timePeriods.items()]
    # print(context_dict['time_periods'])
    context_dict['objects'] = sorted(list(zip(
        range(1, len(objectType)+1), objectType, objectTypeNames, )), key=lambda x: x[2])

    # context_dict['debugTable'] = list(zip(range(1,len(allDebugEvents)+1), displayStudents, displayEvents, displayObject, disaplyTimeStamp))

    return render(request, 'Instructors/DebugSysVars.html', context_dict)


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
        if s.isTestStudent:
            last_Name.append(s.user.last_name + " (Test Student)")
        else:
            last_Name.append(s.user.last_name)
        user_Avatar.append(checkIfAvatarExist(cs))

    return userID, first_Name, last_Name, user_Avatar


def getObjsForSysVarLocal(sysVar):
    objectTypes = ObjectTypes.objectTypes  # enum of system objects
    objIndex = list(sysVar['functions'].keys())
    objNames = []

    for i in objIndex:
        currentObj = objectTypes[i]
        objNames.append(currentObj)

    return objIndex, objNames

def get_object_type_for_periodic_var(variable):
    return [ObjectTypes.none], [ObjectTypes.objectTypes[ObjectTypes.none]]


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def getObjsForSysVar(request):
    objectTypes = ObjectTypes.objectTypes  # enum of system objects
    sysVars = SystemVariable.systemVariables  # enums of system vars
    objects = {}
    is_periodic = False
    if request.POST:
        var_index = int(request.POST['sysVarIndex'])
        if var_index in sysVars:
            var = sysVars[int(var_index)]
            objIndex = list(var['functions'].keys())
        else:
            objIndex = [ObjectTypes.none]
            is_periodic = True
        
        for i in objIndex:
            currentObj = objectTypes[i]
            objects[i] = currentObj

    return JsonResponse({'objects': objects, 'is_periodic': is_periodic})


def getSysValues(student, sysVar, objectType, currentCourse, time_period=None):
    from Badges.events import objectTypesToGetAllFromCourse
    
    values = []
    disaplyData = []

    objString = ObjectTypes.objectTypes[int(objectType)]

    # Get the objects from the db
    if objString == 'challenge':
        chall = Challenges.objects.filter(courseID=currentCourse).order_by(
            'challengeName').values('pk', 'challengeName')
        for x in chall:
            val = calculate_system_variable(
                sysVar, currentCourse, student, int(objectType), x['pk'])
            disaplyData.append(prepForDisplay(
                student, sysVar, objectType, val, x['challengeName'], currentCourse))

    elif objString == 'activity':
        acts = Activities.objects.filter(courseID=currentCourse).order_by(
            'activityName').values('pk', 'activityName')
        for x in acts:
            val = calculate_system_variable(
                sysVar, currentCourse, student, int(objectType), x['pk'])
            disaplyData.append(prepForDisplay(
                student, sysVar, objectType, val, x['activityName'], currentCourse))

    elif objString == 'activityCategory':
        actCats = ActivitiesCategory.objects.filter(
            courseID=currentCourse).exclude(name=uncategorized_activity).order_by('name').values('pk', 'name')
        for x in actCats:
            val = calculate_system_variable(
                sysVar, currentCourse, student, int(objectType), x['pk'])
            disaplyData.append(prepForDisplay(
                student, sysVar, objectType, val, x['name'], currentCourse))

    elif objString == 'topic':
        # ASK ABOUT HOW TO GET A TOPIC
        coruseTopcis = CoursesTopics.objects.filter(courseID=currentCourse).exclude(topicID__topicName=unspecified_topic_name)
        for x in coruseTopcis:
            val = calculate_system_variable(
                sysVar, currentCourse, student, int(objectType), x.topicID.pk)
            disaplyData.append(prepForDisplay(
                student, sysVar, objectType, val, x.topicID.topicName, currentCourse))
    elif objString == 'skill':
        skills = objectTypesToGetAllFromCourse[ObjectTypes.skill](currentCourse)
        for skill in skills:
            val = calculate_system_variable(sysVar, currentCourse, student, int(objectType), skill.pk)
            disaplyData.append(prepForDisplay(student,sysVar,objectType,val,skill.skillName,currentCourse))
    elif objString == 'global':
        if sysVar in SystemVariable.systemVariables:
            val = calculate_system_variable(
                sysVar, currentCourse, student, int(objectType), 0)
            disaplyData.append(prepForDisplay(
                student, sysVar, objectType, val, 0, currentCourse))
        else:
            if not time_period:
                time_period = TimePeriods.beginning_of_time
            print(time_period)
            university = UniversityCourses.objects.filter(courseID=currentCourse).first()
            timezone = university.universityID.universityTimezone

            val = get_periodic_variable_results_for_student(sysVar, time_period, currentCourse.courseID, student,timezone)
            disaplyData.append(prepForDisplay(
                student, sysVar, objectType, val[1], 0, currentCourse))

    return disaplyData


def prepForDisplay(student, sysVar, object, value, assignment, currentCourse):
    name = student.user.first_name + " " + student.user.last_name
    if student.isTestStudent:
        name += " (Test Student)"
    avatarImage = checkIfAvatarExist(StudentRegisteredCourses.objects.get(
        studentID=student, courseID=currentCourse))
    objectName = ObjectTypes.objectTypes[int(object)]
    if sysVar in SystemVariable.systemVariables:
        sysVarName = SystemVariable.systemVariables[int(sysVar)]['name']
    else:
        sysVarName = PeriodicVariables.periodicVariables[int(sysVar)]['name']
    if objectName == 'global':
        assignment = "N/A"
    if type(value) == str and "Error" in value:
        value = "No value available "
    return (name, assignment, objectName, sysVarName, value, avatarImage)
