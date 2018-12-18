'''
Created on Sep 10, 2018

@author: GGM
'''
from django.shortcuts import render
from Instructors.models import Courses
from Badges.models import LeaderboardsConfig
from Instructors.views.utils import initialContextDict, CoursesSkills, Skills
from django.shortcuts import redirect
from Badges.models import CourseConfigParams
from django.contrib.auth.decorators import login_required
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_leaderboard,\
    delete_periodic_task, get_periodic_variable_results
import Students
from Students.models import Student, PeriodicallyUpdatedleaderboards,StudentRegisteredCourses,StudentCourseSkills
from Students.views.avatarView import checkIfAvatarExist
import inspect
import logging
from notify.views import delete
logger = logging.getLogger(__name__)



@login_required
def dynamicLeaderboardView(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict = createTimePeriodContext(context_dict)
    
    if request.method == 'GET':
        leaderboardsConfigs = LeaderboardsConfig.objects.filter(courseID=currentCourse)
        #print(leaderboardsConfigs)
        #if we dont have any leaderboard configs, make a default xp leaderboard
        if leaderboardsConfigs == None:
            createXPLeaderboard(currentCourse)
        else: #otherwise we have items, so we must find out xpLeaderboard
            xpLeaderboard = LeaderboardsConfig.objects.filter(courseID=currentCourse, isXpLeaderboard=True).first()
            if xpLeaderboard:
                context_dict["xpLeaderboardID"] = xpLeaderboard.leaderboardID
                context_dict['leaderboardName'] = xpLeaderboard.leaderboardName
                context_dict['leaderboardDescription'] = xpLeaderboard.leaderboardDescription
                context_dict["numStudentsDisplayed"]= xpLeaderboard.numStudentsDisplayed
                context_dict['timePeriodUpdateInterval'] = xpLeaderboard.timePeriodUpdateInterval
                context_dict['periodicVariable'] = xpLeaderboard.periodicVariable
                context_dict['displayOnCourseHomePage'] = xpLeaderboard.displayOnCourseHomePage
            else:#something horrific happened to our xpLeaderboard so we must recreate it
                createXPLeaderboard(currentCourse)
                
            #now we can create our data for all the dynamic leaderboards
            leaderboardID = []
            leaderboardName = []
            leaderboardUsed = []
            leaderboardDescription = []
            numStudentsDisplayed = []
            periodicVariable = []
            timePeriodUpdateInterval = []
            displayOnHomePage = []
            isContinous = []
            howFarBack = []
            
            #print("leaderboardsConfigs", leaderboardsConfigs)
            leaderboardCount = leaderboardsConfigs.count()
            
            leaderboardsConfigs = LeaderboardsConfig.objects.filter(courseID=currentCourse).exclude(isXpLeaderboard=True)
            #put leaderboard data into the lists
            for leaderboard in leaderboardsConfigs:
                leaderboardID.append(leaderboard.leaderboardID)
                leaderboardName.append(leaderboard.leaderboardName)
                leaderboardDescription.append(leaderboard.leaderboardDescription)
                numStudentsDisplayed.append(leaderboard.numStudentsDisplayed)
                periodicVariable.append(leaderboard.periodicVariable)
                timePeriodUpdateInterval.append(leaderboard.timePeriodUpdateInterval)
                howFarBack.append(leaderboard.howFarBack)
                
                displayOnHomePage.append(leaderboard.displayOnCourseHomePage)
                if leaderboard.isContinous:
                    isContinous.append(True)
                else:
                    isContinous.append(False)
            
            #obtain the checkboxes for the homePageDisplayed    
            homePageCheckboxes = []
            for homePageCheckbox in displayOnHomePage:
                if homePageCheckbox == True:
                    homePageCheckboxes.append('checked')
                else:
                    homePageCheckboxes.append('false')
            
            context_dict['num_tables'] = leaderboardCount    
            context_dict['leaderboard'] = zip(range(2,leaderboardCount+1),leaderboardID ,isContinous, howFarBack,homePageCheckboxes,leaderboardName,leaderboardDescription, timePeriodUpdateInterval, periodicVariable, numStudentsDisplayed )   

        ccparams = context_dict['ccparams']
        
        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID
            
            context_dict["xpWeightSChallenge"]=ccparams.xpWeightSChallenge
            context_dict["xpWeightWChallenge"]=ccparams.xpWeightWChallenge
            context_dict["xpWeightSP"]=ccparams.xpWeightSP
            context_dict["xpWeightAPoints"]=ccparams.xpWeightAPoints
            
                   
        return render(request,'Instructors/DynamicLeaderboard.html', context_dict)
    
    
    if request.method == 'POST':
        
        if 'delete[]' in request.POST:
            deleteLeaderboards = request.POST.getlist('delete[]')
            #print("deleteLeaderboards",deleteLeaderboards)
            deleteLeaderboardConfigObjects(deleteLeaderboards)   
        
        #id of the xp table
        if 'xpLeaderboardID' in request.POST:
            leaderboard = LeaderboardsConfig.objects.get(leaderboardID=request.POST['xpLeaderboardID'])
            leaderboard.leaderboardDescription = request.POST['leaderboardDescription']
            leaderboard.numStudentsDisplayed = int(request.POST['studentsShown'])
            leaderboard.isXpLeaderboard = True
            leaderboard.displayOnCourseHomePage = True
            leaderboard.courseID = currentCourse
            #print("xp board", leaderboard)
            leaderboard.save()
        
            #now we need to cyle though the data for the dynamically generated tables
            
            home = request.POST.getlist('home[]')
            leaderboardID = request.POST.getlist('leaderboardID[]')
            periodicVariableSelected = request.POST.getlist('periodicVariableSelected[]')
            studentsShown= request.POST.getlist('studentsShown[]')
            leaderboardDescription= request.POST.getlist('leaderboardDescription[]')
            timePeriodSelected= request.POST.getlist('timePeriodSelected[]')
            leaderboardName= request.POST.getlist('leaderboardName[]')
            howFarBackTimePeriodSelected = request.POST.getlist('howFarBackTimePeriodSelected_[]')
            
    
#             print("home", home)
#             print("leaderboardID", leaderboardID)
#             print("periodicVariableSelected", periodicVariableSelected)
#             print("studentsShown", studentsShown)
#             print("leaderboardDescription", leaderboardDescription)
#             print("timePeriodSelected", timePeriodSelected)
#             print("leaderboardName", leaderboardName)
#             print("howFarBackTimePeriodSelected", howFarBackTimePeriodSelected)
            
            
            leaderboardObjects = []
            oldPeriodicVariableForLeaderboard = []
            index = 0
            
            for id in leaderboardID:
                resetPeriodicTask = True
                if id != 'none':    
                    leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(id))
                    didStudentsShownChange = (leaderboard.numStudentsDisplayed == int(studentsShown[index]))
                    didTimePeriodUpdateChange = (leaderboard.timePeriodUpdateInterval == int(timePeriodSelected[index]))
                    didPeriodicVariableChange = (leaderboard.periodicVariable == int(periodicVariableSelected[index]))
                    
                    #if they are all the same as the ones in the current leaderboard, dont make a new task
                    if (didStudentsShownChange and didTimePeriodUpdateChange and didPeriodicVariableChange):
                        resetPeriodicTask = False
                else:
                    leaderboard = LeaderboardsConfig()
        
                
                #load all the generic data into the leaderboard
                leaderboard.courseID = currentCourse
                leaderboard.leaderboardName = leaderboardName[index]
                leaderboard.leaderboardDescription = leaderboardDescription[index]
                leaderboard.numStudentsDisplayed = int(studentsShown[index])
                leaderboard.displayOnCourseHomePage = str2bool(home[index])
                
                
                if timePeriodSelected[index] == '0':
                    leaderboard.isContinous = True
                    leaderboard.howFarBack = howFarBackTimePeriodSelected[index]
                    leaderboard.timePeriodUpdateInterval = 0000
                    resetPeriodicTask = False
                    
                    if leaderboard.periodicTask:
                        leaderboard.periodicTask = None
                        delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)  
                    leaderboard.periodicVariable = int(periodicVariableSelected[index])
                else:
                    leaderboard.isContinous = False
                    leaderboard.howFarBack = 0000   
                    leaderboard.timePeriodUpdateInterval = int(timePeriodSelected[index]) 
                    
                    if leaderboard.periodicVariable != 0 and resetPeriodicTask:
                        oldPeriodicVariableForLeaderboard.append(leaderboard.periodicVariable)
                    leaderboard.periodicVariable = int(periodicVariableSelected[index])
                    
                    
                leaderboard.save()
                
                #if we must append because there was a change NOT in name or description
                if resetPeriodicTask:
                    leaderboardObjects.append(leaderboard)
                leaderboard.periodicVariable = int(periodicVariableSelected[index])    
                index= index + 1
            
            createPeriodicTasksForObjects(leaderboardObjects, oldPeriodicVariableForLeaderboard)

        if "ccpID" in request.POST:
            if request.POST['ccpID']:
                ccparams = CourseConfigParams.objects.get(pk=int(request.POST['ccpID']))
            else:
                # Create new Config Parameters
                ccparams = CourseConfigParams()
                ccparams.courseID = currentCourse
            ccpStudentsShown = int(request.POST['studentsShown'])
            ccparams.xpWeightSChallenge = request.POST.get('xpWeightSChallenge')
            ccparams.xpWeightWChallenge = request.POST.get('xpWeightWChallenge')
            ccparams.xpWeightSP = request.POST.get('xpWeightSP')
            ccparams.xpWeightAPoints = request.POST.get('xpWeightAPoints')
            ccparams.leaderboardUpdateFreq = 1
            ccparams.numStudentsDisplayed = ccpStudentsShown
            ccparams.save()
        

        return redirect('/oneUp/instructors/dynamicLeaderboard')
    
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")    
## we must delete and recreate the periodic event or it will break
def createPeriodicTasksForObjects(leaderboards, oldPeriodicVariableForLeaderboard):
    leaderboardToOldPeriodicVariableDict = dict(zip(leaderboards, oldPeriodicVariableForLeaderboard))
    boolNoOldVariable = False

    if len(leaderboardToOldPeriodicVariableDict):
        leaderboardObjects = leaderboardToOldPeriodicVariableDict
        boolNoOldVariable = True
    else:
        leaderboardObjects = leaderboards
         
    for leaderboard in leaderboardObjects:
        if not leaderboard.isContinous:
            if not boolNoOldVariable:
                delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
            else:
                delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboardToOldPeriodicVariableDict[leaderboard], award_type="leaderboard", course=leaderboard.courseID)
            leaderboard.periodicTask = setup_periodic_leaderboard(leaderboard_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, course=leaderboard.courseID, period_index=leaderboard.timePeriodUpdateInterval,  number_of_top_students=leaderboard.numStudentsDisplayed, threshold=1, operator_type='>', is_random=None)
            leaderboard.save()

def deleteLeaderboardConfigObjects(leaderboards):
    for leaderboardObjID in leaderboards:
        leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(leaderboardObjID))
        if leaderboard.periodicVariable != 0:
            delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
        leaderboard.delete()
def createXPLeaderboard(currentCourse):
    xpLeaderboard = LeaderboardsConfig()
    xpLeaderboard.courseID = currentCourse
    xpLeaderboard.leaderboardName = "XP Leaderboard"
    xpLeaderboard.leaderboardDescription = "XP Leaderboard"
    xpLeaderboard.isContinous = True
    xpLeaderboard.isXpLeaderboard = True
    xpLeaderboard.numStudentsDisplayed = 0
    xpLeaderboard.displayOnCourseHomePage = True
    xpLeaderboard.howFarBack = 1502
    xpLeaderboard.periodicVariable = 1403
    xpLeaderboard.save()
def getContinousLeaderboardData(periodicVariable, timePeriodBack, studentsDisplayedNum, courseID):
    ''' This function will get any periodic variable results without the use of celery.
        The timeperiod is used for how many days/minutes to go back from now.
        Ex. Time Period: Weekly - Return results within 7 days ago
        
        Returns list of tuples: [(student, value), (student, value),...]'''
    results = get_periodic_variable_results(periodicVariable, timePeriodBack, courseID.courseID)
    results.sort(key=lambda tup: tup[1], reverse=True)
    results = results[:studentsDisplayedNum]
    results = [(name, score) for name, score in results if score != 0.0 or score != 0]
    return results
def generateSkillTable(currentCourse, context_dict):
    ccparamsList = CourseConfigParams.objects.filter(courseID=currentCourse)
    if len(ccparamsList) > 0:
        ccparams = ccparamsList[0] 
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)
    if st_crs:
        if currentCourse: 
           students = []                                         
           for st_c in st_crs:
               students.append(st_c.studentID)     # all students in the course 
               
               
    # Skill Ranking          
        context_dict['skills'] = []
        cskills = CoursesSkills.objects.filter(courseID=currentCourse)
        for sk in cskills:
            skill = Skills.objects.get(skillID=sk.skillID.skillID)

            usersInfo=[] 
                                             
        for u in students:
            skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=u,skillID = skill)
            skillPoints =0 
                                                 
            for sRecord in skillRecords:
                skillPoints += sRecord.skillPoints

            if skillPoints > 0:
                st_c = StudentRegisteredCourses.objects.get(studentID=u,courseID=currentCourse)                                       
                uSkillInfo = {'user':u.user,'skillPoints':skillPoints,'avatarImage':st_c.avatarImage}
                logger.debug('[GET] ' + str(uSkillInfo))
                usersInfo.append(uSkillInfo)
                
        usersInfo = sorted(usersInfo, key=lambda k: k['skillPoints'], reverse=True)
                 
        if len(usersInfo) != 0:
            skillInfo = {'skillName':skill.skillName,'usersInfo':usersInfo[0:ccparams.numStudentBestSkillsDisplayed]} 
            context_dict['skills'].append(skillInfo) 
        
def generateLeaderboards(currentCourse, displayHomePage):
    
    if displayHomePage:
        leaderboardsConfigs = LeaderboardsConfig.objects.filter(courseID=currentCourse, displayOnCourseHomePage=True)
    else:
        leaderboardsConfigs = LeaderboardsConfig.objects.filter(courseID=currentCourse, displayOnCourseHomePage=False)
        
    leaderboardNames = []
    leaderboardDescriptions = []
    leaderboardRankings = []
    
    for leaderboard in leaderboardsConfigs:
        points = []
        studentFirstNameLastName = []
        avatarImages = []
        hasRecords = False
        
        
        if leaderboard.isContinous:
            results = getContinousLeaderboardData(leaderboard.periodicVariable, leaderboard.howFarBack, leaderboard.numStudentsDisplayed, currentCourse)
            if results:
                hasRecords = True
            for result in results:#result[0] is student object, result[1] is points
                points.append(result[1])
                studentFirstNameLastName.append(result[0].user.first_name +" " + result[0].user.last_name)
                studentRegisteredCourses = StudentRegisteredCourses.objects.get(studentID=result[0],courseID=currentCourse)
                avatarImages.append(studentRegisteredCourses.avatarImage)
                
            
        else:#if its not continuous we must get the data from the database
            leaderboardRecordObjects = PeriodicallyUpdatedleaderboards.objects.filter(leaderboardID=leaderboard).order_by('studentPosition')
            leaderboardRecordObjects = leaderboardRecordObjects[:leaderboard.numStudentsDisplayed+1]
            leaderboardRecords = []
            
            if leaderboardRecordObjects:
                hasRecords = True
            for leaderboardRecordObject in leaderboardRecordObjects:
                if leaderboardRecordObject.studentPoints != 0 or leaderboardRecordObject.studentPoints != 0.0:
                    leaderboardRecords.append(leaderboardRecordObject)
                   
            for leaderboardRecord in leaderboardRecords:
                points.append(leaderboardRecord.studentPoints)
                studentFirstNameLastName.append(leaderboardRecord.studentID.user.first_name +" " + leaderboardRecord.studentID.user.last_name)
                studentRegisteredCoursesObject = StudentRegisteredCourses.objects.get(studentID=leaderboardRecord.studentID, courseID=currentCourse)
                avatarImages.append(studentRegisteredCoursesObject.avatarImage)
                    
        if hasRecords:
            leaderboardRankings.append(zip(range(1,leaderboard.numStudentsDisplayed+1), avatarImages, points, studentFirstNameLastName))
            leaderboardNames.append(leaderboard.leaderboardName)
            leaderboardDescriptions.append(leaderboard.leaderboardDescription)
    return zip(leaderboardNames, leaderboardDescriptions, leaderboardRankings)  
def createTimePeriodContext(context_dict):
    context_dict['periodicVariables'] = [variable for _, variable in PeriodicVariables.periodicVariables.items()]
    timePeriods = [timePeriod for _, timePeriod in TimePeriods.timePeriods.items()]   
    timePeriods.append({
            'index': 0000,
            'name': 'Continuous',
            'displayName': 'Continuous',
            'schedule': lambda: None,
            'datetime': lambda: None
        })
    context_dict['timePeriods']= timePeriods
    timePeriods.reverse()
    return context_dict