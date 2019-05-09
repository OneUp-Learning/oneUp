"""
Django settings for oneUp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import oneUp
import psycopg2.extensions
import getpass
from django.conf.global_settings import LOGIN_URL, STATIC_ROOT, DATE_FORMAT,\
    SESSION_SERIALIZER
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# This is used for uploading AvatarImages
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # This is for the sever
MEDIA_URL = '/media/'  # This is for the html
CKEDITOR_UPLOAD_PATH = "ckeditor/uploads/"
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = True
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_IMAGE_BACKEND = "pillow"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open('/var/www/wsgi-projects/oneUp/oneUp/secret.key') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Logging Levels: DEBUG(Everything) : INFO(Except DEBUG) : WARNING(Except INFO & DEBUG) : ERROR(CRITICAL & ERROR) : CRITICAL(ONLY)
LOGGING_LEVEL = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOGGING_LEVEL
    },
}

ALLOWED_HOSTS = ['oneup.wssu.edu']

# Including the static folder to access it in the urls.py
#MEDIA_ROOT = os.path.join(BASE_DIR, 'static')
#MEDIA_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/'

# Application definition=
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Instructors',
    'Students',
    'Badges',
    'Administrators',
    'Chat',
    'notify',
    'easy_timezones',
    'django_celery_beat',
    'rest_framework',
    'channels',
    'ckeditor',
    'ckeditor_uploader'
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'easy_timezones.middleware.EasyTimezoneMiddleware',
]

ROOT_URLCONF = 'oneUp.urls'

WSGI_APPLICATION = 'oneUp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

with open('/var/www/wsgi-projects/oneUp/oneUp/prodDBpassword.txt') as f:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'oneup',
            'USER': 'oneupuser',
            'PASSWORD': f.read().strip(),
            'HOST': 'localhost',
            'PORT': '',
            'OPTIONS': {
                'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
            }
        }
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

FIXTURE_DIRS = ()

STATIC_PATH = os.path.join(BASE_DIR, 'static')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/' # You may find this is already defined as such.

CKEDITOR_BASEPATH = os.path.join(STATIC_ROOT, 'ThirdParty/ckeditor/ckeditor')

STATICFILES_DIRS = (
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

GEOIP_DATABASE = os.path.join(BASE_DIR, 'GeoLiteCity.dat')
GEOIPV6_DATABASE = os.path.join(BASE_DIR, 'GeoLiteCityv6.dat')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# = '/static/'

# Authentication related settings

# Changes the list of password hashes to prioritize BCryptSHA256.  Note that this requires the django[bcrypt] to be installed.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

LOGIN_URL = '/oneUp/permission_error'

# Ckeditor Settings
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_Custom': [
            {'name': 'document', 'items': [
                'Source', '-', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': [
                'Cut', 'Copy', 'Paste', 'PasteText', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', 'SelectAll']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'EqnEditor', 'CodeSnippet', 'Markdown']},
            '/',
            {'name': 'styles', 'items': [
                'Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'about', 'items': ['About']},
        ],
        'toolbar': 'Custom',  # put selected toolbar config here
        # 'height': 291,
        'width': '100%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        'format_tags': 'p;h1;h2;h3;pre',
        'removeDialogTabs': 'image:advanced;link:advanced',
        'line_height': '0.8em;1em;1.1em;1.2em;1.3em;1.4em;1.5em',
        'autoParagraph': False,
        'tabSpaces': 4,
        'codeSnippet_theme': 'default',
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'uploadwidget',
            'eqneditor',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'pastecode',
            'pastefromword',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
            'smiley',
            'codesnippet',
            'markdown'
        ]),
    }
}

# For chat/celery
rabbitmq_username = getpass.getuser()
with open('oneUp/rabbitmq_password') as f:
    rabbitmq_password = f.read().strip()

# Chat app settings
ASGI_APPLICATION = 'oneUp.routing.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
        "CONFIG": {
            "host": 'amqp://'+rabbitmq_username+':'+rabbitmq_password+'@localhost/asgi',
        },
    },
}
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

# Custom serializer which is mostly just JSON, but can handle decimal types
# without making them floats along the way.
SESSION_SERIALIZER = 'oneUp.jsonSerializerExtension.OneUpExtendedJSONSerializer'

# Celery Settings
CELERY_BROKER_URL = 'amqp://'+rabbitmq_username+':'+rabbitmq_password+'@localhost/'+rabbitmq_username
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_IMPORTS = ['Badges.periodicVariables']
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
# Turns celery on or off in oneUp code.
# Note that this is not automatic, but enabled by statements in our
# code which check its value.  Turning it on or off will only effect
# oneUp code which uses "if CELERY_ENABLED:" statements
CELERY_ENABLED = True

CURRENTLY_MIGRATING = False
