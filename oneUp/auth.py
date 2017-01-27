'''
This is where the code which sets up the authorization rules is housed.

Created on Aug 18, 2014

@author: kirwin
'''

from django.contrib.auth.models import Group, Permission, User
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType

user_content_type = ContentType.objects.get_for_model(User)

createTeachers, created = Permission.objects.get_or_create(name='Create Teachers', codename='cr_teacher', content_type=user_content_type)
createStudents, created = Permission.objects.get_or_create(name='Create Students', codename='cr_student', content_type=user_content_type)
createAdmins, created = Permission.objects.get_or_create(name='Create Admins', codename='cr_admin', content_type=user_content_type)

admins, created = Group.objects.get_or_create(name='Admins')
admins.permissions.add(createTeachers, createStudents, createAdmins)

teachers, created = Group.objects.get_or_create(name='Teachers')
teachers.permissions.add(createStudents)

def checkPermBeforeView(perm, request, view):
    if request.user.hasPerm(perm):
        return view(request);
    else:
        return render_to_response("permission_error.html")
