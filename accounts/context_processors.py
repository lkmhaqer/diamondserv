"""
file: accounts/context_processors.py
author: lkmhaqer

source: https://stackoverflow.com/q/433162/
"""
import socket
from django.conf import settings

def app_version(request):
  """ return some constants from our settings file """
  environment = {
    'BRANCH': settings.APP_BRANCH,
    'VERSION': settings.APP_VERSION,
    'SERVER_NAME': socket.gethostname(),
  }
  return environment
