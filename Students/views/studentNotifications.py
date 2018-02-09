'''
Created on Aug 28, 2017

@author: jevans116
'''
from django.shortcuts import render
from django.http import JsonResponse
from Students.models import StudentActivities
from Students.views.utils import studentInitialContextDict
from Instructors.models import Activities
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from notify.models import Notification
from datetime import datetime
from Students.models import Student
from Instructors.views.utils import initialContextDict


from django.contrib.auth.decorators import login_required
from lib2to3.main import diff_texts

@login_required
def studentNotifications(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    if request.user.is_authenticated():
        sID = Student.objects.filter(user=request.user).exists()
        if(sID):
            context_dict,currentCourse = studentInitialContextDict(request)
            context_dict['is_teacher'] = False
        else:
            context_dict, currentCourse = initialContextDict(request)
            context_dict['is_teacher'] = True

        
      
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']

        
        if(request.GET['ID'] == "1"):
            context_dict['ID'] = 1
        elif(request.GET['ID'] == "2"):
            context_dict['ID'] = 2
        else:
            context_dict['ID'] = 0
            
    else:
        print('ID is 0')
        context_dict['ID'] = 0
        
    context_dict['request'] = request

    return render(request,'notifications/all.html', context_dict)

def updateNotificationTable(request):
    flag = request.GET.get('flag', None)
    last_notification = int(flag) if flag.isdigit() else None
    
    if last_notification:
        new_notifications = request.user.notifications.filter(
                id__gt=last_notification).active().prefetch()
        
        notification_list = []
        timeStamps = []
        for nf in new_notifications:
            notification = nf.as_json()
            notification_list.append(notification)
#             convertTime(nf.created.timestamp())
            
            timeStamps.append(nf.created.timestamp())
            
        ctx = {
            "retrieved": len(new_notifications),
            "unread_count": request.user.notifications.unread().count(),
            "notifications": notification_list,
            "timeStamps": timeStamps,
            "success": True,
        }

        return JsonResponse(ctx)
    
    else:
        msg = _("Notification flag not sent.")

    ctx = {"success": False, "msg": msg}
    return JsonResponse(ctx)    

def convertTime(Time):
    diff = (datetime.utcnow() - Time) / 1000
    timeString = ""
    
    monthDifference = diff
    monthDifference = (60 * 60 * 24 * 7 * 4)
    monthDifference = abs(round(monthDifference));

    weekDifference = diff
    weekDifference /= (60 * 60 * 24 * 7)
    weekDifference = abs(round(weekDifference))
    
    dayDifference = diff
    dayDifference /= (60 * 60 * 24)
    dayDifference = abs(round(dayDifference))
    
    hoursDifference = diff;          
    hoursDifference /= (60 * 60);
    hoursDifference =  abs(round(hoursDifference))
 
    minutesDifference = diff;            
    minutesDifference /= 60;
    minutesDifference = abs(round(minutesDifference))
    
    if(monthDifference == 0 and weekDifference == 0 and dayDifference == 0 and hoursDifference == 0
       and minutesDifference == 0):
        return "0 minutes"
    else:
        if(monthDifference != 0):
            if(monthDifference == 1):
                return "1 month"
            else:
                return str(monthDifference) + " months"
        
        if(weekDifference != 0):
            if(weekDifference == 1):
                timeString = "1 week, "
            else:
                timeString = str(weekDifference) + " weeks, "
                
        if(dayDifference !=0):
            if(dayDifference != 1):
                pass
 
 
#      return [daysDifference, hoursDifference, minutesDifference ];

    

        
        
            
            
            
            
            
            
            
            
            
            
