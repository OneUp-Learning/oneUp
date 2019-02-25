#
# Created on  2/18/2019
# James Cherry
#Modeled after announcementCreateView.py
#
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.utils import utcDate, initialContextDict

#2.18.2019 JC
from Students.models import StudentGoalSetting
from Badges.enums import Goal

@login_required
 
def goalCreate(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)

    if request.POST:

        # Get the activity from the DB for editing or create a new announcement  
        if 'studentGoalID' in request.POST:
            sg = request.POST['studentGoalID']
            goal= StudentGoalSetting.objects.get(pk=int(sg))
        else:
            goal = StudentGoalSetting()

        #     
        goal.goalType = request.POST['goalType']
        goal.vcRuleID = request.POST['vcRuleID']
        goal.objectID = request.POST['objectID']
        goal.targetedNumber = request.POST['targetNumber']
        goal.timestamp = utcDate()
        
        goal.save();  #Writes to database.    
                
        return redirect('goalsList')

    ######################################
    # request.GET 
    else:
        if request.GET:
                            
            # If studentGoalId is specified then we load for editing.
            if 'studentGoalID' in request.GET:
                goal = StudentGoalSetting.objects.get(pk=int(request.GET['studentGoalID']))
                
                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['studentGoalID'] = request.GET['studentGoalID']
                context_dict['goalType'] = goal.goalType
                context_dict['targetNumber'] = goal.targetNumber
                                

    return render(request,'Students/GoalsCreationForm.html', context_dict)
