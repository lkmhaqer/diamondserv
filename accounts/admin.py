"""
file: accounts/admin.py
author: lkmhaqer
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import InviteCode, MinecraftUser, User


class CustomUserAdmin(UserAdmin):
  """ Our object for extending UserAdmin with our fields. """
  fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('server_limit',)}),)
  add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('server_limit',)}),)

admin.site.register(User, CustomUserAdmin)
admin.site.register(MinecraftUser)
admin.site.register(InviteCode)
