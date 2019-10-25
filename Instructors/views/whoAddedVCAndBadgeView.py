'''
Created on Oct 5, 2019

@author: GGM
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.views.utils import initialContextDict, utcDate
from oneUp.decorators import instructorsCheck
from Badges.models import BadgesVCLog, CourseConfigParams


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def whoAddedBadgeAndVC(request):

    context_dict, currentCourse = initialContextDict(request)
    
    if request.method == 'GET':
        logObjectList = []
        loggedObjects = BadgesVCLog.objects.filter(courseID=currentCourse)
        ccParam = CourseConfigParams.objects.get(courseID = currentCourse)
        
        for loggedObject in loggedObjects:
            if loggedObject.studentBadges and ccParam.badgesUsed:
                logObjectList.append(loadDataIntoList(loggedObject, 'Badge'))

            if loggedObject.studentVirtualCurrency and ccParam.virtualCurrencyUsed:
                logObjectList.append(loadDataIntoList(loggedObject, 'VC'))

        context_dict['loggedObjects'] = logObjectList

    return render(request, 'Instructors/WhoAddedBadgeAndVC.html', context_dict)


##function to hold all the different things
def loadDataIntoList(loggedObject, badgeOrVc):
    logDict ={
        'issuer':loggedObject.issuer.get_full_name(),
        'time':loggedObject.timestamp
    }
    if badgeOrVc == 'Badge':
        logDict.update({'student':loggedObject.studentBadges.studentID.user.get_full_name(),
                        'objectNameOrAmount':loggedObject.studentBadges.badgeID.badgeName,
                        'object':'Badge'})

    if badgeOrVc == 'VC':
        logDict.update({'student':loggedObject.studentVirtualCurrency.studentID.user.get_full_name(),
                        'objectNameOrAmount':loggedObject.studentVirtualCurrency.value,
                        'object':'VCRule: ' +loggedObject.studentVirtualCurrency.vcRuleID.vcRuleName})

    return logDict
