"""
file: wrangler/admin.py
author: lkmhaqer
"""
from django.contrib import admin

from .models import EnvironmentVar, MineHost, Server, ServerType


admin.site.register(MineHost)
admin.site.register(Server)
admin.site.register(EnvironmentVar)
admin.site.register(ServerType)
