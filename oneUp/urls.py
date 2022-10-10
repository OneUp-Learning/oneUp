from django.conf.urls import include, url
from django.urls import path
from django.conf import settings

from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
import django.views.static
from django.views.generic import TemplateView


admin.autodiscover()

if settings.CURRENTLY_MIGRATING:
    urlpatterns = []
else:
    urlpatterns = [
        # Examples:
        #url(r'^$', 'oneUp.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        path('admin/', admin.site.urls),
        url(r'^oneUp/instructors/', include('Instructors.urls')),
        url(r'^oneUp/students/', include('Students.urls')),
        url(r'^oneUp/badges/', include('Badges.urls')),
        url(r'^oneUp/administrators/',include('Administrators.urls')),
        url(r'^oneUp/chat/', include('Chat.urls')),
        url(r'^oneUp/trivia/', include('Trivia.urls')),
        url(r'^oneUp/',include('Administrators.urls')),
        url(r'^login$', LoginView.as_view(template_name='home.html'), name='login'),
        url(r'^notifications/', include('notify.urls', 'notifications')),
        url(r'^ckeditor/', include('ckeditor_uploader.urls')),
        path('service-worker.js',(TemplateView.as_view(
            template_name="Chat/service-worker.js",
            content_type='application/javascript')), name='service-worker.js'),
        path('trivia-service-worker.js',(TemplateView.as_view(
            template_name="Trivia/service-worker.js",
            content_type='application/javascript')), name='service-worker.js'),
        url(r'^$', RedirectView.as_view(url="/oneUp/home"))
    ]


# if settings.DEBUG:
#         urlpatterns += patterns(
#                 'django.views.static',
#                 (r'media/(?P<path>.*)',
#                 'serve',
#                 {'document_root': settings.MEDIA_ROOT}), 
#         )

#settings to include the static folder using the MEDIA_ROOT declared in the settings.py file
if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),
        url(r'^media/(?P<path>.*)$', django.views.static.serve,{'document_root': settings.MEDIA_ROOT}),
    ]
