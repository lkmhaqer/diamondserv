"""
file: accounts/tests/test_views.py
author: lkmhaqer

Mostly integration tests, ensuring we see the responses we want.
"""
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from accounts.models import InviteCode, User


class InviteUserRegistrationFormTests(TestCase):
  """ Testing errors and validation in our form. """
  def setUp(self):
    self.invite = InviteCode(email='test@phukish.com')
    self.invite.save()
    self.user = User(username='test', password='testfest', email='foo@bar.com')
    self.user.save()

  def test_valid_invite_code(self):
    """ Test that the invite registration form accepts a token. """
    response = self.client.get(reverse(
      'accounts:invite_registration',
      args=[self.invite.token]
    ))

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertContains(response, self.invite.token)

  def test_invalid_uuid_invite_code(self):
    """
    Test that if you use an invalid uuid for
    invite code, we return the form with an error.
    """
    response = self.client.post(
      reverse(
        'accounts:invite_registration',
        args=[self.invite.token]
      ),
      {
        'username': 'test2',
        'email': 'test2@phukish.com',
        'password1': 'testPass',
        'password2': 'testPass',
        'invite_token': 'fjnuidsahi'
      }
    )

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertFormError(
      response,
      'form',
      'invite_token',
      'Invite code not found.',
    )

  def test_valid_uuid_invalid_invite_code(self):
    """
    Test that given a valid uuid, but invalid invite code is rejected.
    We create an invalid token string, and check that it doesn't match
    the one generated in setUp.
    """
    invalid_token = '00000000-0000-0000-0000-000000000000'
    if self.invite.token == '00000000-0000-0000-0000-000000000000':
      invalid_token = '00000000-0000-0000-0000-000000000001'

    response = self.client.post(
      reverse(
        'accounts:invite_registration',
        args=[self.invite.token]
      ),
      {
        'username': 'test2',
        'email': 'test2@phukish.com',
        'password1': 'testPass',
        'password2': 'testPass',
        'invite_token': invalid_token
      }
    )

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertFormError(
      response,
      'form',
      'invite_token',
      'Invite code not found.',
    )

  def test_no_duplicate_username(self):
    """
    Test that the page returns the form with an error
    for a duplicate username.
    """
    response = self.client.post(
      reverse(
        'accounts:invite_registration',
        args=[self.invite.token]
      ),
      {
        'username': 'test',
        'email': 'test2@phukish.com',
        'password1': 'testPass',
        'password2': 'testPass',
        'invite_token': self.invite.token
      }
    )

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertFormError(
      response,
      'form',
      'username',
      'This username is already taken.',
    )

  def test_no_duplicate_email(self):
    """
    Test that the page returns the form with an error
    for a duplicate username.
    """
    response = self.client.post(
      reverse(
        'accounts:invite_registration',
        args=[self.invite.token]
      ),
      {
        'username': 'test2',
        'email': 'foo@bar.com',
        'password1': 'testPass',
        'password2': 'testPass',
        'invite_token': self.invite.token
      }
    )

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertFormError(
      response,
      'form',
      'email',
      'This email has been used already.',
    )

  def test_required_email(self):
    """ Test that email is a required field. """
    response = self.client.post(
      reverse(
        'accounts:invite_registration',
        args=[self.invite.token]
      ),
      {
        'username': 'test2',
        'email': '',
        'password1': 'testPass',
        'password2': 'testPass',
        'invite_token': self.invite.token
      }
    )

    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertFormError(
      response,
      'form',
      'email',
      'A valid email address is required.',
    )
