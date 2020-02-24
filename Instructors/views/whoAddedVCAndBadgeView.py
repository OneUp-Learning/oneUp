'''
Created on Oct 5, 2019

@author: GGM
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.utils import initialContextDict, utcDate
from oneUp.decorators import instructorsCheck
from Badges.models import BadgesVCLog, CourseConfigParams, ActionArguments
from Chat.serializers import UserSerializer
import json


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def whoAddedBadgeAndVC(request):

    context_dict, currentCourse = initialContextDict(request)
    
    if request.method == 'GET':
        logObjectList = []
        loggedObjects = BadgesVCLog.objects.filter(courseID=currentCourse).order_by('-timestamp')
        ccParam = CourseConfigParams.objects.get(courseID = currentCourse)
        
        for loggedObject in loggedObjects:
            data = json.loads(loggedObject.log_data)
            result = {}
            if data['issuer'] == "System":
                result['issuer'] = data['issuer']
            else:
                result['issuer'] = f"{data['issuer']['first_name']} {data['issuer']['last_name']}"

            result['student'] = f"{data['student']['first_name']} {data['student']['last_name']}"
            result['time'] = loggedObject.timestamp

            if 'badge' in data and ccParam.badgesUsed:
                result['badge'] = data['badge'] 

            if 'vc' in data and ccParam.virtualCurrencyUsed:
                result['vc'] = data['vc']
            
            logObjectList.append(result)

        context_dict['loggedObjects'] = logObjectList

    return render(request, 'Instructors/WhoAddedBadgeAndVC.html', context_dict)

def create_badge_vc_log_json(issuer, student_obj, log_type, log_sub_type, vc_award_type="Add"):
    ''' Creates json object for BadgesVCLog
        issuer -> User object
        student_obj -> either
        log_type -> "Badge" or "VC"
        log_sub_type -> "Automatic" or "Manual" or "Time-Period" or "Callout" or "Duel"
    '''
    result = {}
    if issuer == "System":
        result['issuer'] = issuer
    else:
        result['issuer'] = UserSerializer(issuer).data

    if log_type == 'Badge':
        result['student'] = UserSerializer(student_obj.studentID.user).data
        result['badge'] = {'name': student_obj.badgeID.badgeName, 'type': log_sub_type}

    elif log_type == 'VC':
        result['student'] = UserSerializer(student_obj.studentID.user).data
        if log_sub_type == 'Automatic':
            value = -1
            if ActionArguments.objects.filter(ruleID=student_obj.vcRuleID.ruleID).exists():
                value = ActionArguments.objects.filter(ruleID=student_obj.vcRuleID.ruleID)[0].argumentValue

            result['vc'] = {'name': student_obj.vcRuleID.vcRuleName, 'value': value, 'type': log_sub_type}
        elif log_sub_type == 'Manual':
            result['vc'] = {'name': student_obj.vcRuleID.vcRuleName, 'value': student_obj.value, 'type': f"{vc_award_type} {log_sub_type}" }
        else:
            result['vc'] = {'name': student_obj.vcName, 'value': student_obj.value, 'type': log_sub_type}
    
    return result
