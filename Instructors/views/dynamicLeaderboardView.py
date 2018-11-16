'''
Created on Sep 10, 2018

@author: GGM
'''
from django.shortcuts import render
from Instructors.models import Courses
from Badges.models import LeaderboardsConfig
from Instructors.views.utils import initialContextDict
from django.shortcuts import redirect
from Badges.models import CourseConfigParams
from django.contrib.auth.decorators import login_required
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_leaderboard,\
    delete_periodic_task, get_periodic_variable_results
import Students
from Students.models import Student, PeriodicallyUpdatedleaderboards,StudentRegisteredCourses




@login_required
def dynamicLeaderboardView(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict = createTimePeriodContext(context_dict)
    
    if request.method == 'GET':
        leaderboardsConfigs = LeaderboardsConfig.objects.filter(courseID=currentCourse)
        print(leaderboardsConfigs)
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
            
            print("leaderboardsConfigs", leaderboardsConfigs)
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
        
        #id of the xp table
        if request.POST['xpLeaderboardID']:
            leaderboard = LeaderboardsConfig.objects.get(leaderboardID=request.POST['xpLeaderboardID'])
            leaderboard.leaderboardDescription = request.POST['leaderboardDescription']
            leaderboard.numStudentsDisplayed = int(request.POST['studentsShown'])
            leaderboard.isXpLeaderboard = True
            leaderboard.displayOnCourseHomePage = True
            leaderboard.courseID = currentCourse
            print("xp board", leaderboard)
            leaderboard.save()
        
        #now we need to cyle though the data for the dynamically generated tables
        deleteLeaderboards = request.POST.getlist('delete[]')
        home = request.POST.getlist('home[]')
        leaderboardID = request.POST.getlist('leaderboardID[]')
        periodicVariableSelected = request.POST.getlist('periodicVariableSelected[]')
        studentsShown= request.POST.getlist('studentsShown[]')
        leaderboardDescription= request.POST.getlist('leaderboardDescription[]')
        timePeriodSelected= request.POST.getlist('timePeriodSelected[]')
        leaderboardName= request.POST.getlist('leaderboardName[]')
        howFarBackTimePeriodSelected = request.POST.getlist('howFarBackTimePeriodSelected_[]')
        
        print(deleteLeaderboards)
        print(home)
        print(periodicVariableSelected)
        print(studentsShown)
        print(leaderboardDescription)
        print(timePeriodSelected)
        print(leaderboardName)
        print(howFarBackTimePeriodSelected)
        
        leaderboardObjects = []
        index = 0
        resetPeriodicTask = True
        for id in leaderboardID:
            
            if id != 'none':    
                leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(id))
                
                didStudentsShownChange = (leaderboard.numStudentsDisplayed == int(studentsShown[index]))
                didLeaderboardChange = (leaderboard.timePeriodUpdateInterval == int(timePeriodSelected[index]))
                didPeriodicVariableChange = (leaderboard.periodicVariable == int(periodicVariableSelected[index]))
                
                #if they are all the same as the ones in the current leaderboard, dont make a new task
                if (didStudentsShownChange and didLeaderboardChange and didPeriodicVariableChange):
                    resetPeriodicTask = False
            else:
                leaderboard = LeaderboardsConfig()
    
            
            #load all the generic data into the leaderboard
            leaderboard.courseID = currentCourse
            leaderboard.leaderboardName = leaderboardName[index]
            leaderboard.leaderboardDescription = leaderboardDescription[index]
            leaderboard.numStudentsDisplayed = int(studentsShown[index])
            leaderboard.periodicVariable = int(periodicVariableSelected[index])
            leaderboard.displayOnCourseHomePage = str2bool(home[index])
            
            if timePeriodSelected[index] == '0':
                leaderboard.isContinous = True
                leaderboard.howFarBack = howFarBackTimePeriodSelected[index]
            else:
                leaderboard.timePeriodUpdateInterval = int(timePeriodSelected[index])
                
            leaderboard.save()
            
            #if we must append because there was a change NOT in name or description
            if resetPeriodicTask:
                leaderboardObjects.append(leaderboard)
                
            index= index + 1
        
        createPeriodicTasksForObjects(leaderboardObjects)
        deleteLeaderboardConfigObjects(deleteLeaderboards)   
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
def createPeriodicTasksForObjects(leaderboards):
    for leaderboard in leaderboards:
        if not leaderboard.isContinous:
            delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
            leaderboard.periodicTask = setup_periodic_leaderboard(leaderboard_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, course=leaderboard.courseID, period_index=leaderboard.timePeriodUpdateInterval,  number_of_top_students=leaderboard.numStudentsDisplayed, threshold=1, operator_type='>', is_random=None)
            leaderboard.save()

def deleteLeaderboardConfigObjects(leaderboards):
    for leaderboardObjID in leaderboards:
        leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(leaderboardObjID))
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
    xpLeaderboard.howFarBack = 1500
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
def generateLeaderboards(currentCourse, displayHomePage, context_dict):
    
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
        
        leaderboardNames.append(leaderboard.leaderboardName)
        leaderboardDescriptions.append(leaderboard.leaderboardDescription)
        if leaderboard.isContinous:
            results = getContinousLeaderboardData(leaderboard.periodicVariable, leaderboard.howFarBack, leaderboard.numStudentsDisplayed, currentCourse)
            for result in results:#result[0] is student object, result[1] is points
                points.append(result[1])
                studentFirstNameLastName.append(result[0].user.first_name +" " + result[0].user.last_name)
                studentRegisteredCourses = StudentRegisteredCourses.objects.get(studentID=result[0],courseID=currentCourse)
                avatarImages.append(studentRegisteredCourses.avatarImage)
        else:#if its not continuous we must get the data from the database
            leaderboardRecords = PeriodicallyUpdatedleaderboards.objects.filter(leaderboardID=leaderboard).order_by('studentPosition')
            for leaderboardRecord in leaderboardRecords:
                points.append(leaderboardRecord.studentPoints)
                studentFirstNameLastName.append(leaderboardRecord.studentID.user.first_name +" " + leaderboardRecord.studentID.user.last_name)
                avatarImages.append(leaderboardRecord.studentID.user.avatarImage)
                  
        leaderboardRankings.append(zip(range(1,leaderboard.numStudentsDisplayed+1), avatarImages, points, studentFirstNameLastName))
        
    return zip(leaderboardNames, leaderboardDescriptions, leaderboardRankings)  
def createTimePeriodContext(context_dict):
    context_dict['periodicVariables'] = [variable for _, variable in PeriodicVariables.periodicVariables.items()]
    timePeriods = [timePeriod for _, timePeriod in TimePeriods.timePeriods.items()]   
    timePeriods.append({
            'index': 0000,
            'name': 'Continous',
            'displayName': 'Continous',
            'schedule': lambda: None,
            'datetime': lambda: None
        })
    context_dict['timePeriods']= timePeriods
    timePeriods.reverse()
    return context_dict