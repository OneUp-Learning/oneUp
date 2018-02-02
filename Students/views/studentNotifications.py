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


from django.contrib.auth.decorators import login_required

@login_required
def studentNotifications(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict,currentCourse = studentInitialContextDict(request)
    print(context_dict)
      
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0

    if 'currentCourseID' in request.session:                
        currentCourse = request.session['currentCourseID']                
        studentId = context_dict['student'] #get student
        
        #Use the options to do querys
    
        
#         return render(request,'notifications/includes/default.html', context_dict)
    context_dict['request'] = request

    return render(request,'notifications/all.html', context_dict)

def updateNotificationTable(request):
    flag = request.GET.get('flag', None)
    last_notification = int(flag) if flag.isdigit() else None
    
    if last_notification:
        new_notifications = request.user.notifications.filter(
                id__gt=last_notification).active().prefetch()
        
        notification_list = []
        for nf in new_notifications:
            notification = nf.as_json()
            notification_list.append(notification)
            
        ctx = {
            "retrieved": len(new_notifications),
            "unread_count": request.user.notifications.unread().count(),
            "notifications": notification_list,
            "success": True,
        }

        return JsonResponse(ctx)
    
    else:
        msg = _("Notification flag not sent.")

    ctx = {"success": False, "msg": msg}
    return JsonResponse(ctx)
        
        
            
            
            
            
            
            
            
            
            
            
