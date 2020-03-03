import sys
import os
from django.conf import settings

if 'test' in sys.argv:
    # Setup static files to work for test server
    settings.STATIC_ROOT = ''
    settings.STATICFILES_DIRS = [os.path.join(settings.BASE_DIR, 'static')]
    settings.STATIC_URL = '/static/'