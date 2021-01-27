"""
file: accounts/views.py
author: lkmhaqer
"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import InviteUserRegistrationForm, MinecraftUserForm, UserRegistrationForm
from .models import User


def _get_registration_form(post=None, invite_token=None):
  """ get the current registration form based on invite settings. """
  if settings.INVITE_ONLY:
    return InviteUserRegistrationForm(post, initial={'invite_token': f'{invite_token}'})
  return UserRegistrationForm(post)

def user_registration(request, invite_token=None):
  """ User registration view  """
  if settings.INVITE_ONLY and invite_token is None:
    return render(request, 'accounts/registration_closed.html')

  if request.method == 'POST':
    form = _get_registration_form(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('login'))
  else:
    form = _get_registration_form(post=None, invite_token=invite_token)

  return render(request, 'accounts/registration.html', {'form': form})

@login_required
def add_minecraft_user(request):
  """ Create a Server """
  if request.method == 'POST':
    form = MinecraftUserForm(request.POST, user=request.user)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('accounts:user_detail'))

  else:
    form = MinecraftUserForm()

  return render(request, 'accounts/add_minecraft_user.html', {'form': form})

@login_required
def user_detail(request):
  """ Return a profile page for the current logged in user """
  user = get_object_or_404(User, pk=request.user.id)
  return render(request, 'accounts/detail.html', {'user': user})
