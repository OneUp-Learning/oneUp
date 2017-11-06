#
# Created on  03/10/2015
# DD
#
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from Instructors.models import Activities, Courses
from Instructors.views.activityListView import createContextForActivityList
from Instructors.views.utils import initialContextDict

@login_required
def activityCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)
    string_attributes = ['activityName','description','points','instructorNotes'];
    
    
    if request.POST:

        # Get the activity from the DB for editing or create a new activity  
        if 'activityID' in request.POST:
            ai = request.POST['activityID']
            activity = Activities.objects.get(pk=int(ai))
        else:
            activity = Activities()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(activity,attr,request.POST[attr])
        
        activity.courseID = currentCourse; 
        if 'fileUpload' in request.POST:
            activity.isFileAllowed = True
        else:
            activity.isFileAllowed = False
            
                  
       # get the author                            
        if request.user.is_authenticated():
            activity.author = request.user.username
        else:
            activity.author = ""

        activity.save();  #Writes to database.
         
        return render(request,'Instructors/ActivitiesList.html', context_dict)

    ######################################
    # request.GET 
    else:
        if request.GET:
                            
            # If questionId is specified then we load for editing.
            if 'activityID' in request.GET:
                activity = Activities.objects.get(pk=int(request.GET['activityID']))

                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['activityID'] = request.GET['activityID']
                for attr in string_attributes:
                    context_dict[attr]=getattr(activity,attr)

    return render(request,'Instructors/ActivityCreateForm.html', context_dict)
