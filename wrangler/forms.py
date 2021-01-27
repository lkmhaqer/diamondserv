"""
file: wrangler/forms.py
author: lkmhaqer
"""
from django.db.models import Count, F
from django.forms import ModelForm, ModelMultipleChoiceField, ModelChoiceField

from accounts.models import MinecraftUser

from .models import MineHost, ServerType, Server


class ServerForm(ModelForm):
  """ The form for users to interface with the server object. """
  class Meta:
    model = Server
    fields = ['name', 'host', 'game_type', 'server_type', 'op_list']

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(ServerForm, self).__init__(*args, **kwargs) # pylint: disable=R1725

    # For the host field, we want to locate all hosts that have less servers
    # than their self-defined server_limit.
    self.fields['host'] = ModelChoiceField(
      queryset=MineHost.objects.annotate(
          server_count=Count('server')
        ).filter(server_count__lt=F('server_limit'), enabled=True),
      required=True,
    )
    self.fields['server_type'] = ModelChoiceField(
      queryset=ServerType.objects.filter(enabled=True).order_by('name'),
      required=True,
    )
    self.fields['op_list'] = ModelMultipleChoiceField(
      queryset=MinecraftUser.objects.filter(owner=self.user),
      required=False,
    )

  def clean(self):
    if self.user.server_set.count() >= self.user.server_limit:
      self.add_error(
        None,
        f'You are only allowed {self.user.server_limit} servers.'
      )

  def save(self, commit=True):
    server = super(ServerForm, self).save(commit=False) # pylint: disable=R1725
    server.owner = self.user
    if commit:
      server.save()
      self.save_m2m()

    return server
