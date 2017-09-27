from django.conf.urls import url
from django.contrib import admin

#from Administrators.views.createAdminView import createAdminViewUnchecked
#from Administrators.views.createTeacherView import createTeacherViewUnchecked
from Administrators.views.loginView import loginView
from Administrators.views.courseListView import courseListView
from Administrators.views.setCourseView import setCourseView
from Administrators.views.setUserView import setUserView
from Administrators.views.aboutUsView import aboutUsView
from Administrators.views.sitemapView import sitemap
from Administrators.views.contactUsView import contactUsView
from Administrators.views.createCourse import courseCreateView
from Administrators.views.deleteCourse import courseDeleteView
from Administrators.views.deleteTeacher import teacherDeleteView
from Administrators.views.adminHomeView import adminHome
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^adminHome', adminHome, name='adminHomeView'),
 #   url(r'^createAdmin', createAdminViewUnchecked, name='createAdminView'),
 #   url(r'^createTeacher', createTeacherViewUnchecked, name='createTeacherView'),
    url(r'^createCourse', courseCreateView, name='courseCreateView'),
    url(r'^deleteCourse', courseDeleteView, name='courseDeleteView'),
    url(r'^deleteTeacher', teacherDeleteView, name='teacherDeleteView'),
    url(r'^home', loginView, name='loginView'),
    url(r'^courses', courseListView, name='courseListView'),
    url(r'^setCourse', setCourseView, name='setCourseView'),
    url(r'^user', setUserView, name='setUserView'),
    url(r'^aboutUs', aboutUsView, name='aboutUs'),
    url(r'^sitemap', sitemap, name='sitemap'),
    url(r'^contact-us', contactUsView, name='contact-us'),
]
