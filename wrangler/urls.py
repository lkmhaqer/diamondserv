"""
file: wrangler/urls.py
author: lkmhaqer
"""
from django.urls import path

from . import views


app_name = 'wrangler'
urlpatterns = [
  path('', views.index, name='index'),
  path('page/<slug:template>', views.page, name='page'),
  path('status/', views.status, name='status'),
  path('status/<str:username>', views.status, name='user_status'),
  path(
    'server/create',
    views.server_create,
    name='server_create'
  ),
  path(
    'server/<slug:server_name>/delete',
    views.server_delete,
    name='server_delete'
  ),
  path(
    'server/<slug:server_name>/restart',
    views.server_restart,
    name='server_restart'
  ),
  path(
    'server/<slug:server_name>/detail',
    views.server_detail,
    name='server_detail'
  ),
]
