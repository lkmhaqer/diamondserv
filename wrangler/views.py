"""
file: wrangler/views.py
author: lkmhaqer
"""
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.template import TemplateDoesNotExist
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, render

from accounts.models import User

from .forms import ServerForm
from .models import Server
from .tasks import (
  docker_delete_server,
  docker_restart_server,
  docker_start_server,
  docker_get_logs,
  minecraft_status
)


def index(request):
  """ our root page response """
  return render(request, 'wrangler/index.html')

@login_required
def page(request, template):
  """ Return a given template page where no context is needed. """
  try:
    response = render(request, f'wrangler/{template}.html')
  except TemplateDoesNotExist as err:
    raise Http404 from err
  return response

@login_required
def server_create(request):
  """ Create a Server """
  if request.method == 'POST':
    form = ServerForm(request.POST, user=request.user)
    if form.is_valid():
      server = form.save()
      server = form.instance
      docker_start_server(server)
      return HttpResponseRedirect(reverse('wrangler:server_detail', args=[server.name]))

  else:
    form = ServerForm(user=request.user)

  return render(request, 'wrangler/server_create.html', {'form': form})

@login_required
def server_delete(request, server_name):
  """ Delete a Server """
  if request.method == 'POST':
    server = get_object_or_404(Server, name=server_name)
    if not request.user == server.owner:
      raise PermissionDenied
    docker_delete_server(server)
    server.delete()

  return HttpResponseRedirect(reverse(
    'wrangler:user_status', args=[request.user.username]
  ))

@login_required
def server_restart(request, server_name):
  """ Restart a server """
  if request.method == 'POST':
    server = get_object_or_404(Server, name=server_name)
    if not request.user == server.owner:
      raise PermissionDenied
    docker_restart_server(server)

  return HttpResponseRedirect(reverse(
    'wrangler:user_status', args=[request.user.username]
  ))

@login_required
def server_detail(request, server_name):
  """ Show the details for a server. """
  server = get_object_or_404(Server, name=server_name)
  query = minecraft_status([server])
  query_info, server_status = query['serverlist'][0]

  safe_logs = []
  if request.user == server.owner:
    logs = docker_get_logs(server)
    logs = logs.splitlines()
    safe_logs = [l.decode('utf-8') for l in logs]

  context = {
    'server': server,
    'logs': safe_logs,
    'status': server_status,
    'query_info': query_info
  }

  return render(request, 'wrangler/server_detail.html', context)

def status(request, username=None):
  """ list out servers and show status. """
  if username:
    user = get_object_or_404(User, username=username)
    if not request.user == user:
      raise PermissionDenied
    server_list = Server.objects.filter(owner=user.id)
    template = 'user_status'
  else:
    server_list = Server.objects.all()
    template = 'status'

  servers = minecraft_status(server_list)
  context = {
    'servers': servers['serverlist'],
    'total_players': servers['total_players'],
    'total_capacity': servers['total_capacity']
  }

  return render(request, f'wrangler/{template}.html', context)
