import os
import sys

path = '/var/www/OMFraF'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'omfraf.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
