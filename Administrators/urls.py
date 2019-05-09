from django.conf.urls import url
from django.contrib import admin

from Administrators.views.createAdminView import createAdminView
from Administrators.views.createTeacherView import createTeacherView
from Administrators.views.loginView import loginView
from Administrators.views.courseListView import courseListView
from Administrators.views.setCourseView import setCourseView
from Administrators.views.setUserView import setUserView
from Administrators.views.createCourse import courseCreateView
from Administrators.views.deleteItem import deleteItemView
from Administrators.views.adminHomeView import adminHome
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^adminHome', adminHome, name='adminHomeView'),
    url(r'^createAdmin', createAdminView, name='createAdminView'),
    url(r'^createTeacher', createTeacherView, name='createTeacherView'),
    url(r'^createCourse', courseCreateView, name='courseCreateView'),
    url(r'^deleteItem', deleteItemView, name='deleteItemView'),
    url(r'^home', loginView, name='loginView'),
    url(r'^courses', courseListView, name='courseListView'),
    url(r'^setCourse', setCourseView, name='setCourseView'),
    url(r'^user', setUserView, name='setUserView'),
]
