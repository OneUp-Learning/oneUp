'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.template import RequestContext
from django.shortcuts import render

from oneUp.auth import createAdmins, checkPermBeforeView, admins
from django.contrib.auth.models import User

def createAdminView(request):
    checkPermBeforeView(createAdmins,request,createAdminViewUnchecked)

def createAdminViewUnchecked(request):
 
    context_dict = { 'usertype':'Administrator', 'message':'' }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # Get all the administrators (AH)
    administrators = User.objects.filter(groups__name='Admins')
    print(administrators)
    context_dict['administrators'] = administrators
    
    if request.POST:
        uname = request.POST['uname']
        pword = request.POST['pword']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        
        user = User.objects.create_user(uname,email,pword)
        user.first_name = firstname
        user.last_name = lastname
        user.groups.add(admins)
        user.save()
        
        context_dict['message'] = '<B>New Administrator '+uname+' created!</B>'
        
        return render(request,"Administrators/createAdmin.html", context_dict)
    else:
        
        return render(request,"Administrators/createAdmin.html", context_dict)

