from django.shortcuts import render
from Badges.enums import SystemVariable, system_variable_type_to_HTML_type, ObjectTypes
from Instructors.models import Activities, Challenges, Courses
from Instructors.views.utils import initialContextDict

def conditionTestView(request):
    context_dict,current_course = initialContextDict(request);
    
    # Things to add to context dictionary:
    #     variables
    var_list = []
    for sysVarIndex in SystemVariable.systemVariables.keys():
        sysVarTable = SystemVariable.systemVariables[sysVarIndex]
        sysVar = {
            "id":sysVarIndex,
            "name":sysVarTable["displayName"],
            "tooltip":sysVarTable["description"],
            "type":system_variable_type_to_HTML_type[sysVarTable["type"]],
            "objects":[ObjectTypes.objectTypes[x] for x in sysVarTable["objectsDefinedFor"]],
        }
        var_list.append(sysVar)
    context_dict['variables'] = var_list

    chall_list = [{"id":ch.challengeID,"name":ch.challengeName} for ch in Challenges.objects.filter(courseID = current_course)]
    act_list = [{"id":act.activityID,"name":act.activityName} for act in Activities.objects.filter(courseID = current_course)]
    
    context_dict['objectTypes'] = [{"name":"challenge","plural":"challenges","objects":chall_list },
                                   {"name":"activity","plural":"activities", "objects":act_list}]
    context_dict['defaultObject'] = "challenge"
    
    return render(request,'Badges/conditionInterface.html', context_dict)
