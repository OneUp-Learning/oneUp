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
from django.conf.global_settings import LOGIN_URL, STATIC_ROOT, DATE_FORMAT
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#This is used for uploading AvatarImages
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') #This is for the sever
MEDIA_URL =  'media/' #This is for the html


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6l1(5i-qm34-eb!@un9gc%(g$o^=rgw8l++0!o9t6-^($qi6&k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
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
    'notify',
    'easy_timezones',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'easy_timezones.middleware.EasyTimezoneMiddleware',
)

ROOT_URLCONF = 'oneUp.urls'

WSGI_APPLICATION = 'oneUp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS' : [ os.path.join(BASE_DIR, 'templates') ],
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

STATIC_PATH = os.path.join(BASE_DIR,'static')

STATIC_ROOT = os.path.join(BASE_DIR,'static')

STATIC_URL = '/OneUp/' # You may find this is already defined as such.

STATICFILES_DIRS = (
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

GEOIP_DATABASE = os.path.join(BASE_DIR,'GeoLiteCity.dat')
GEOIPV6_DATABASE = os.path.join(BASE_DIR,'GeoLiteCityv6.dat')


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

LOGIN_URL='/oneUp/permission_error'

