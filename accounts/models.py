"""
file: accounts/models.py
author: lkmhaqer
"""
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
  """
  Custom user model as suggested by the Django documentation.
  https://docs.djangoproject.com/en/3.1/topics/auth/customizing/
  """
  email = models.EmailField(default='', unique=True)
  server_limit = models.IntegerField(default=2)


class MinecraftUser(models.Model):
  """ A minecraft username, tied to an account. """
  name = models.CharField(max_length=16)
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )

  def __str__(self):
    return f'{self.name}'


class InviteCode(models.Model):
  """ A one-time use invite code in UUID form. """
  email = models.EmailField(unique=True)
  token = models.UUIDField(default=uuid.uuid4, editable=False)
  used = models.BooleanField(default=False)

  def __str__(self):
    if self.used:
      return f'{self.email} (Used)'
    reg_url = reverse(
      'accounts:invite_registration',
      kwargs={'invite_token': self.token}
    )
    return f'https://mc.phukish.com{reg_url}'
