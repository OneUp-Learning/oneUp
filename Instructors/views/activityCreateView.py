#
# Created on  03/10/2015
# DD
#
import os
from datetime import datetime
from decimal import *

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from Badges.conditions_util import (databaseConditionToJSONString,
                                    setUpContextDictForConditions)
from Badges.models import CourseConfigParams
from Instructors.models import (Activities, ActivitiesCategory,
                                UploadedActivityFiles)
from Instructors.views.utils import (current_localtime, datetime_to_selected,
                                     initialContextDict, str_datetime_to_local)
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def activityCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict, currentCourse = initialContextDict(request)
    context_dict = setUpContextDictForConditions(
        context_dict, currentCourse, None)
    string_attributes = ['activityName',
                         'description', 'points', 'instructorNotes']
    actCats = ActivitiesCategory.objects.filter(courseID=currentCourse)
    context_dict['categories'] = actCats

    if request.POST:

        # Get the activity from the DB for editing or create a new activity
        if 'activityID' in request.POST:
            ai = request.POST['activityID']
            activity = Activities.objects.get(pk=int(ai))
        else:
            activity = Activities()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            if attr == "points":
                if "points" in request.POST and request.POST[attr]:
                    setattr(activity, attr, request.POST[attr])
                else:
                    setattr(activity, attr, Decimal(0.0))
            else:
                setattr(activity, attr, request.POST[attr])

        activity.courseID = currentCourse

        print(ActivitiesCategory.objects.filter(courseID=currentCourse))

        if request.POST['actCat']:
            if ActivitiesCategory.objects.filter(pk=request.POST['actCat'], courseID=currentCourse):
                activity.category = ActivitiesCategory.objects.filter(
                    pk=request.POST['actCat'], courseID=currentCourse).first()
            else:
                activity.category = ActivitiesCategory.objects.filter(
                    name="Uncategorized", courseID=currentCourse).first()
        else:
            activity.category = ActivitiesCategory.objects.filter(
                name="Uncategorized", courseID=currentCourse).first()

        if 'isGraded' in request.POST:
            activity.isGraded = True
        else:
            activity.isGraded = False

        if 'fileUpload' in request.POST:
            activity.isFileAllowed = True
        else:
            activity.isFileAllowed = False

        # Set the number of attempts
        if 'attempts' in request.POST:
            attempts = request.POST['attempts']
            if attempts == '':
                activity.uploadAttempts = 9999
            else:
                activity.uploadAttempts = request.POST['attempts']

        # Set the start date and end data to show the activity
        #print(str_datetime_to_local(request.POST['startTime']))
        try:
            activity.startTimestamp = datetime.strptime(request.POST['startTime'], "%m/%d/%Y %I:%M %p") 
            activity.hasStartTimestamp = True
            
        except ValueError:
            activity.hasStartTimestamp = False

        try:
            activity.endTimestamp = datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M %p") 
            activity.hasEndTimestamp = True
        except ValueError:
            activity.hasEndTimestamp = False

        try:
            activity.deadLine = datetime.strptime(request.POST['deadLine'], "%m/%d/%Y %I:%M %p") 
            activity.hasDeadline = True
        except ValueError:
            activity.hasDeadline = False

        # get the author
        if request.user.is_authenticated:
            activity.author = request.user.username
        else:
            activity.author = ""

        activity.save()  # Writes to database.
        print('activity')
        print(activity)

        print('Starting Files' + str(len(request.FILES)))
        # Check to see if there are any files that need to be handled and linked to activity
        if len(request.FILES) != 0:
            print('In the file section')
            files = request.FILES.getlist('actFile')
            makeFilesObjects(request.user, files, activity)

        print('End Files')

        return redirect('/oneUp/instructors/activitiesList')

    ######################################
    # request.GET
    else:

        # If questionId is specified then we load for editing.
        if 'activityID' in request.GET:
            activity = Activities.objects.get(
                pk=int(request.GET['activityID']))

            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            context_dict['activityID'] = request.GET['activityID']
            for attr in string_attributes:
                context_dict[attr] = getattr(activity, attr)
            context_dict["points"] = int(context_dict["points"])

            context_dict['currentCat'] = activity.category
            context_dict['categories'] = ActivitiesCategory.objects.filter(
                courseID=currentCourse)

            # ggm upload attempts infinite
            if activity.uploadAttempts == 9999:
                context_dict['uploadAttempts'] = ''
            else:
                context_dict['uploadAttempts'] = activity.uploadAttempts
            context_dict['isFileUpload'] = activity.isFileAllowed
            context_dict['isGraded'] = activity.isGraded

            
            if activity.hasStartTimestamp:
                context_dict['startTimestamp'] = datetime_to_selected(activity.startTimestamp)
            else:
                context_dict['startTimestamp'] = ""
            
            if activity.hasEndTimestamp:
                context_dict['endTimestamp'] = datetime_to_selected(activity.endTimestamp)
            else:
                context_dict['endTimestamp'] = ""
            
            if activity.hasDeadline:
                context_dict['deadLineTimestamp'] = datetime_to_selected(activity.deadLine)
            else:
                context_dict['deadLineTimestamp'] = ""


            activityFiles = UploadedActivityFiles.objects.filter(
                activity=activity, latest=True)
            if(activityFiles):
                context_dict['activityFiles'] = activityFiles
            else:
                print('No activity files found')
        else:
            ccp = CourseConfigParams.objects.get(courseID=currentCourse)
            if ccp.hasCourseStartDate and ccp.courseStartDate <= current_localtime().date():
                # print(type(ccp.courseStartDate))
                context_dict['startTimestamp'] = datetime_to_selected(ccp.courseStartDate) 
            if ccp.hasCourseEndDate and ccp.courseEndDate > current_localtime().date(): 
                context_dict['endTimestamp'] = datetime_to_selected(ccp.courseEndDate) 
                context_dict['deadLineTimestamp'] = datetime_to_selected(ccp.courseEndDate)

    return render(request, 'Instructors/ActivityCreateForm.html', context_dict)


def makeFilesObjects(instructorID, files, activity):

    # Get the old files and see if any of the new files match it
    #oldActFile = UploadedActivityFiles.objects.filter(activityFileCreator=instructorID, activity=activity)

    for i in range(0, len(files)):  # make student files so we can save files to hardrive
        print('Makeing file object ' + str(files[i].name))
        actFile = UploadedActivityFiles()
        actFile.activity = activity
        actFile.activityFile = files[i]
        actFile.activityFileCreator = instructorID
        actFile.save()
        actFile.activityFileName = os.path.basename(actFile.activityFile.name)
        actFile.save()


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def removeFileFromActivty(request):
    if request.user.is_authenticated:
        print('IS A USER')
    else:
        return HttpResponse(403)

    if request.POST:
        if 'fileID' in request.POST:
            fID = request.POST['fileID']
            currentFile = UploadedActivityFiles.objects.get(ID=fID)
            currentFile.activityFile.delete()
            currentFile.delete()
            print('File deleted')
            return HttpResponse(200)

    return HttpResponse(403, 'something went wrong')
