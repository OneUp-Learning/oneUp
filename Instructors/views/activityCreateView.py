#
# Created on  03/10/2015
# DD
#
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.utils import timezone
from Instructors.models import Activities, UploadedActivityFiles, ActivitiesCategory
from Instructors.views.utils import utcDate, initialContextDict, localizedDate
from Badges.conditions_util import databaseConditionToJSONString, setUpContextDictForConditions
from Badges.models import CourseConfigParams
from Instructors.constants import default_time_str
from datetime import datetime
import os
from oneUp.decorators import instructorsCheck
from decimal import *


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

        default_date = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        # Set the start date and end data to show the activity
        if(request.POST['startTime'] == ""):
            activity.startTimestamp = default_date
        elif datetime.strptime(request.POST['startTime'], "%m/%d/%Y %I:%M %p"):
            activity.startTimestamp = localizedDate(
                request, request.POST['startTime'], "%m/%d/%Y %I:%M %p")
        else:
            activity.startTimestamp = default_date

        # if user does not specify an expiration date, it assigns a default value really far in the future
        # This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            activity.endTimestamp = default_date
        elif datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M %p"):
            activity.endTimestamp = localizedDate(
                request, request.POST['endTime'], "%m/%d/%Y %I:%M %p")
        else:
            activity.endTimestamp = default_date

        if(request.POST['deadLine'] == ""):
            activity.deadLine = default_date
        elif datetime.strptime(request.POST['deadLine'], "%m/%d/%Y %I:%M %p"):
            activity.deadLine = localizedDate(
                request, request.POST['deadLine'], "%m/%d/%Y %I:%M %p")
        else:
            activity.deadLine = default_date

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

            startTime = localizedDate(request, str(timezone.make_naive(activity.startTimestamp.replace(
                microsecond=0))), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %I:%M %p")
            if activity.startTimestamp.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") != default_time_str:
                context_dict['startTimestamp'] = startTime
            else:
                context_dict['startTimestamp'] = ""

            endTime = localizedDate(request, str(timezone.make_naive(activity.endTimestamp.replace(
                microsecond=0))), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %I:%M %p")
            if activity.endTimestamp.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") != default_time_str:
                context_dict['endTimestamp'] = endTime
            else:
                context_dict['endTimestamp'] = ""
            # Make naive to get rid of offset and convert it to localtime what was set before in order to display it
            deadLine = localizedDate(request, str(timezone.make_naive(activity.deadLine.replace(
                microsecond=0))), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %I:%M %p")
            if activity.deadLine.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") != default_time_str:
                context_dict['deadLineTimestamp'] = deadLine
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
            if ccp.courseStartDate < timezone.now().date():
                context_dict['startTimestamp'] = ccp.courseStartDate.strftime(
                    "%m/%d/%Y %I:%M %p")
            if ccp.courseEndDate > timezone.now().date():
                context_dict['endTimestamp'] = ccp.courseEndDate.strftime(
                    "%m/%d/%Y %I:%M %p")
                context_dict['deadLineTimestamp'] = ccp.courseEndDate.strftime(
                    "%m/%d/%Y %I:%M %p")

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
