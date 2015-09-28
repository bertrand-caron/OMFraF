from os import environ
from os.path import dirname
from sys import path

path = dirname(__file__)
if path not in path:
    path.append(path)

environ['DJANGO_SETTINGS_MODULE'] = 'omfraf.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
