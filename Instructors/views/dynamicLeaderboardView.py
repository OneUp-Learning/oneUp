'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses
from Badges.models import LeaderboardsConfig
from Instructors.views.utils import initialContextDict
from django.shortcuts import redirect
from Badges.models import CourseConfigParams
from django.contrib.auth.decorators import login_required
from Badges.periodicVariables import PeriodicVariables, TimePeriods, setup_periodic_leaderboard,\
    delete_periodic_task
import Students
from Students.models import Student
from venv import create


@login_required


def dynamicLeaderboardView(request):
 
    context_dict, currentCourse = initialContextDict(request)
    context_dict = createTimePeriodContext(context_dict)
    
    if request.method == 'GET':
        leaderboardsConfigs = LeaderboardsConfig.objects.filter(courseID=currentCourse)
        print(leaderboardsConfigs)

        #it is implied the first leaderboardConfig is the one for the course
        if(leaderboardsConfigs):
            leaderboardID = []
            leaderboardName = []
            leaderboardUsed = []
            leaderboardDescription = []
            numStudentsDisplayed = []
            periodicVariable = []
            timePeriodUpdateInterval = []
            displayOnHomePage = []
            studCanChangeLeaderboardVis = []
            checked = []
            print("leaderboardsConfigs", leaderboardsConfigs)
            leaderboardCount = leaderboardsConfigs.count()
            
            #put leaderboard data into the lists
            for leaderboard in leaderboardsConfigs:
                leaderboardID.append(leaderboard.leaderboardID)
                leaderboardName.append(leaderboard.leaderboardName)
                leaderboardUsed.append(leaderboard.leaderboardUsed)
                leaderboardDescription.append(leaderboard.leaderboardDescription)
                numStudentsDisplayed.append(leaderboard.numStudentsDisplayed)
                periodicVariable.append(leaderboard.periodicVariable)
                timePeriodUpdateInterval.append(leaderboard.timePeriodUpdateInterval)
                displayOnHomePage.append(leaderboard.leaderboardDisplayPage)
                studCanChangeLeaderboardVis.append(leaderboard.studCanChangeLeaderboardVis)
                if(int(leaderboard.timePeriodUpdateInterval) == 000):
                    checked.append('checked')
                else:
                    checked.append('false')
                
                
            #we must pop the first one off as its the leaderboard XP table
            context_dict["leaderboardID"] = leaderboardID.pop(0)
            context_dict['leaderboardName'] = leaderboardName.pop(0)
            context_dict['leaderboardUsed'] = leaderboardUsed.pop(0)
            context_dict['leaderboardDescription'] = leaderboardDescription.pop(0)
            context_dict['checked'] = checked.pop(0)
            context_dict["numStudentsDisplayed"]= numStudentsDisplayed.pop(0)
            context_dict['timePeriodUpdateInterval'] = timePeriodUpdateInterval.pop(0)
            context_dict['periodicVariable'] = periodicVariable.pop(0)
            context_dict['leaderboardDisplayPage'] = displayOnHomePage.pop(0)
            context_dict['studCanChangeLeaderboardVis'] = studCanChangeLeaderboardVis.pop(0)
            
            
            homePageCheckboxes = []
            for homePageCheckbox in displayOnHomePage:
                print(homePageCheckbox)
                if homePageCheckbox == True:
                    homePageCheckboxes.append('checked')
                else:
                    homePageCheckboxes.append('false')
            
                
            context_dict['leaderboard'] = zip(range(2,leaderboardCount+1),leaderboardID ,checked , homePageCheckboxes,leaderboardName,leaderboardDescription, timePeriodUpdateInterval, periodicVariable, numStudentsDisplayed )   
            
            
              
        else:
            leaderboardCount = 1
        ccparams = context_dict['ccparams']
        
        if ccparams:
            context_dict['ccpID'] = ccparams.ccpID
            context_dict['num_tables'] = leaderboardCount
            context_dict["xpWeightSChallenge"]=ccparams.xpWeightSChallenge
            context_dict["xpWeightWChallenge"]=ccparams.xpWeightWChallenge
            context_dict["xpWeightSP"]=ccparams.xpWeightSP
            context_dict["xpWeightAPoints"]=ccparams.xpWeightAPoints
            
                   
        return render(request,'Instructors/DynamicLeaderboard.html', context_dict)
    
    
    if request.method == 'POST':
        
        if request.POST['numLeaderTables']:
            numLeaderTables = int(request.POST['numLeaderTables'])
        
        #if we have an id for the first leaderboaard(XP leaderboard), then get the id
        if request.POST['leaderboardID']:
            leaderboard = LeaderboardsConfig.objects.get(leaderboardID=request.POST['leaderboardID'])
        else:#therwise dont get the id.
            leaderboard = LeaderboardsConfig()
        
        #regardless of what happens we still need to get the data for the xp table    
        leaderboard.leaderboardDescription = request.POST['leaderboardDescription']
        ccpStudentsShown = leaderboard.numStudentsDisplayed = int(request.POST['studentsShown'])
        leaderboard.timePeriodUpdateInterval = 000
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
        cont= request.POST.getlist('cont[]')
        
        print(deleteLeaderboards)
        print(home)
        print(periodicVariableSelected)
        print(studentsShown)
        print(leaderboardDescription)
        print(timePeriodSelected)
        print(leaderboardName)
        print(cont)
        
        leaderboardObjects = []
        ##first we need to iterate over the ids and find out if it has an object already, thus its an edit
        index = 0
        for id in leaderboardID:
            
            if id != 'none':    
                leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(id))
            else:#therwise dont get the id, its a new object
                leaderboard = LeaderboardsConfig()
    
            
            #load all the generic data into the leaderboard
            leaderboard.courseID = currentCourse
            leaderboard.leaderboardName = leaderboardName[index]
            leaderboard.leaderboardDescription = leaderboardDescription[index]
            leaderboard.numStudentsDisplayed = int(studentsShown[index])
            leaderboard.periodicVariable = int(periodicVariableSelected[index])
            leaderboard.leaderboardDisplayPage = str2bool(home[index])
            
            if cont[index] == 'true':
                leaderboard.timePeriodUpdateInterval = 000
            else:
                leaderboard.timePeriodUpdateInterval = int(timePeriodSelected[index])
            leaderboard.save()
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
        delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
        leaderboard.periodicTask = setup_periodic_leaderboard(leaderboard_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, course=leaderboard.courseID, period_index=leaderboard.timePeriodUpdateInterval,  number_of_top_students=leaderboard.numStudentsDisplayed, threshold=1, operator_type='>', is_random=None)
        leaderboard.save()

def deleteLeaderboardConfigObjects(leaderboards):
    for leaderboardObjID in leaderboards:
        leaderboard = LeaderboardsConfig.objects.get(leaderboardID=int(leaderboardObjID))
        delete_periodic_task(unique_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, award_type="leaderboard", course=leaderboard.courseID)
        leaderboard.delete()
def createTimePeriodContext(context_dict):

    context_dict['periodicVariables'] = [variable for _, variable in PeriodicVariables.periodicVariables.items()]
    context_dict['timePeriods'] = [timePeriod for _, timePeriod in TimePeriods.timePeriods.items()]        
    return context_dict