'''
This view is for creating new administrative accounts.

Created on Aug 18, 2014

@author: kirwin
'''

from django.template import RequestContext
from django.shortcuts import render

from oneUp.auth import createAdmins, checkPermBeforeView, admins
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import adminsCheck


@login_required
@user_passes_test(adminsCheck,login_url='/oneUp/home',redirect_field_name='')
def createAdminView(request):
 
    context_dict = {}
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
    
    if request.method == 'POST':
        uname = request.POST['administratorUsername']
        pword = request.POST['administratorPassword']
        firstname = request.POST['administratorFirstName']
        lastname = request.POST['administratorLastName']
        email = request.POST['administratorEmail']
        
        administrators = User.objects.filter(groups__name="Admins", username=uname)
        administratorEmails = User.objects.filter(groups__name="Admins", email= email)
        errorList = []
        if 'adminID' in request.GET:
            if uname == request.POST['aUsernamePrev'] and email == request.POST['aEmailPrev']: # If the username and email has not been changed
                administrator = administrators[0]
                administrator.first_name = firstname
                administrator.last_name = lastname
                if not pword.startswith('bcrypt'):
                    administrator.set_password(pword)
                administrator.save()
            if administrators and administrators[0].username != request.POST['aUsernamePrev']: 
                errorList.append("administrator username is taken.")
            if administratorEmails and administratorEmails[0].email != request.POST['aEmailPrev']:
                errorList.append("administrator email is taken.")
            if len(errorList) == 0: # The username and email are unique
                administrator = administrators[0]
                administrator.username = uname
                administrator.first_name = firstname
                administrator.last_name = lastname
                administrator.email = email
                if not pword.startswith('bcrypt'):
                    administrator.set_password(pword)
                administrator.save()
        else: # Creating a new admin
            if administrators:
                errorList.append("Administrator username is taken.")
            if administratorEmails:
                errorList.append("Administrator email is taken.")
            if len(errorList) == 0:
                user = User.objects.create_user(uname,email,pword)
                
                user.first_name = firstname
                user.last_name = lastname
                user.groups.add(admins)
                user.save()
                
        context_dict['errorMessages'] = errorList
        
    context_dict['view'] = False
    administrators = User.objects.filter(groups__name='Admins')
    context_dict['administrators'] = administrators
    if 'adminID' in request.GET:
        administrator = User.objects.get(groups__name="Admins", username=request.GET['adminID'])
        context_dict['administratorUsername'] = administrator.username
        context_dict['administratorPassword'] = administrator.password
        context_dict['administratorFirstName'] = administrator.first_name
        context_dict['administratorLastName'] = administrator.last_name
        context_dict['administratorEmail'] = administrator.email
        
        context_dict['editAdmin'] = True
        
    return render(request,"Administrators/createAdmin.html", context_dict)

