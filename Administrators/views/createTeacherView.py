'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.template import RequestContext
from django.shortcuts import render

from oneUp.auth import createTeachers, checkPermBeforeView, teachers
from django.contrib.auth.models import User


def createTeacherView(request):
    checkPermBeforeView(createTeachers,request,createTeacherViewUnchecked)

def createTeacherViewUnchecked(request):
    context_dict = { 'usertype':'Teacher', 'message':'' }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # Get all the instructors (AH)
    instructors = User.objects.filter(groups__name='Teachers')
    print("Instructors:", instructors)
    context_dict['instructors'] = instructors
        
    if request.POST:
        uname = request.POST['uname']
        pword = request.POST['pword']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        
        user = User.objects.create_user(uname,email,pword)
        user.first_name = firstname
        user.last_name = lastname
        user.groups.add(teachers)
        user.save()
        
        context_dict['message'] = '<B>New Teacher '+uname+' created!</B>'
        
        return render(request,"Administrators/createTeacher.html", context_dict)
    else:
        return render(request,"Administrators/createTeacher.html", context_dict)

