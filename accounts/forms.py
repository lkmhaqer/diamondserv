"""
file: wrangler/forms.py
author: lkmhaqer
"""
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, UUIDField

from .models import InviteCode, MinecraftUser, User


class MinecraftUserForm(ModelForm):
  """ The form for users to add minecraft usernames to their profile. """
  class Meta:
    model = MinecraftUser
    fields = ['name']

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(MinecraftUserForm, self).__init__(*args, **kwargs) # pylint: disable=R1725

  def save(self, commit=True):
    minecraft_name = super(MinecraftUserForm, self).save(commit=False) # pylint: disable=R1725
    minecraft_name.owner = self.user
    if commit:
      minecraft_name.save()

    return minecraft_name


class UserRegistrationForm(UserCreationForm):
  """ Regular form for users to register with. """
  def clean(self):
    username = self.cleaned_data['username']
    if User.objects.filter(username=username).exists():
      self.add_error('username', 'This username is already taken.')
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).exists():
      self.add_error('email', 'This email has been used already.')

  class Meta(UserCreationForm):
    model = User
    fields = ['username', 'email']


class InviteUserRegistrationForm(UserRegistrationForm):
  """ Registration form with an invite code that must be checked. """
  invite_token = UUIDField()

  def __init__(self, *args, **kwargs): # pylint: disable=W0231
    self.invite = None
    super(InviteUserRegistrationForm, self).__init__(*args, **kwargs) # pylint: disable=R1725

  def clean(self):
    try:
      self.invite = InviteCode.objects.get(
        token=self.cleaned_data['invite_token'],
        used=False
        )
    except (InviteCode.DoesNotExist, KeyError):
      self.add_error('invite_token', 'Invite code not found.')
    username = self.cleaned_data['username']
    if User.objects.filter(username=username).exists():
      self.add_error('username', 'This username is already taken.')
    if 'email' in self.cleaned_data:
      email = self.cleaned_data['email']
      if User.objects.filter(email=email).exists():
        self.add_error('email', 'This email has been used already.')
    else:
      self.add_error('email', 'A valid email address is required.')

  def save(self, commit=True):
    self.invite.used = True
    self.invite.save()
    return super(InviteUserRegistrationForm, self).save(commit=True) # pylint: disable=R1725

  class Meta(UserRegistrationForm.Meta):
    model = User
    