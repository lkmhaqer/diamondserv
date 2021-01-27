"""
file: wrangler/models.py
author: lkmhaqer
"""
from django.conf import settings
from django.db import models

from accounts.models import MinecraftUser


class GameType(models.IntegerChoices):
  """ Minecraft standard game types """
  SURVIVAL = 0
  CREATIVE = 1


class EnvironmentVar(models.Model):
  """ A stored instance of an ENV_VAR for use with ServerType """
  name = models.CharField(max_length=255)
  value = models.CharField(max_length=255)

  def __str__(self):
    return f'{self.name}={self.value}'


class MineHost(models.Model):
  """
  Represents an instance of a minecraft hosting box,
  where multiple Server() objects may live.
  """
  name = models.CharField(max_length=255, unique=True)
  enabled = models.BooleanField(default=True)
  server_limit = models.IntegerField(default=7)
  min_port = models.IntegerField(default=25565)
  max_port = models.IntegerField(default=25693)

  def __str__(self):
    return f'{self.name}'


class ServerType(models.Model):
  """
  The type of server, and related attributtes.
  """
  name = models.CharField(max_length=255)
  enabled = models.BooleanField(default=True)
  version = models.CharField(default='', max_length=255)
  docker_image = models.CharField(max_length=255)
  environment_vars = models.ManyToManyField(EnvironmentVar, blank=True)

  class Meta:
    unique_together = ('name', 'version')

  def __str__(self):
    return f'{self.name} ({self.version})'


class Server(models.Model):
  """
  Our server object, this represents an instance of a
  minecraft server that contains all the attributes
  needed to launch this server instance.
  """
  name = models.SlugField(max_length=32, unique=True)
  host = models.ForeignKey(MineHost, on_delete=models.CASCADE)
  op_list = models.ManyToManyField(MinecraftUser, blank=True)
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )
  game_type = models.IntegerField(
    choices=GameType.choices,
    default=GameType.SURVIVAL
  )
  # ServerType(id=1) is a default 'Vanilla' added by migration 0001
  server_type = models.ForeignKey(
    ServerType,
    on_delete=models.CASCADE,
    default=1
  )
  port = models.IntegerField(
    blank=True,
    null=True,
  )

  class Meta:
    unique_together = ('host', 'port')

  def __str__(self):
    return f'{self.name} ({self.host.name}:{self.port})'

  def save(self, force_insert=False, force_update=False, using=None,
    update_fields=None):
    """
    If this is our first time saving the record,
    set the port to the next available value
    in the host's min_port to max_port range.
    This can be overwritten if port is specified
    in the Server object when you create it.
    """
    if not self.pk and not self.port:
      port_list = list(
        self.__class__.objects.filter(host=self.host)
        .values_list('port', flat=True)
      )
      self.port = next(
        p for p in range(self.host.min_port, self.host.max_port) if p not in port_list
      )

    super().save()

  def get_socket(self):
    """ return just the host:port socket URI """
    return f'{self.host.name}:{self.port}'
