'''
Created on Feb 20, 2015

Last updated on Sep 12, 2016
'''
from django.template import RequestContext
from django.shortcuts import redirect

def setCourseView(request):
 
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        
    if request.POST:
        request.session['currentCourseID'] = request.POST['courseID']

    user = request.user    
    if user.groups.filter(name='Teachers').exists():
        context_dict["is_teacher"] = True
        return redirect('instructorCourseHome')
    elif user.groups.filter(name='Admins').exists():
        context_dict["is_admin"] = True
        return redirect('adminHomeView')
    else:
        context_dict["is_student"] = True
        return redirect('StudentCourseHome')

    
 