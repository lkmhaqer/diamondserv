"""
file: accounts/urls.py
author: lkmhaqer
"""
from django.urls import path

from . import views


app_name = 'accounts'
urlpatterns = [
  path('detail', views.user_detail, name='user_detail'),
  path('register', views.user_registration, name='user_registration'),
  path(
    'register/<uuid:invite_token>',
    views.user_registration,
    name='invite_registration'
  ),
  path(
    'add_minecraft_user',
    views.add_minecraft_user,
    name='add_minecraft_user'
  ),
]
