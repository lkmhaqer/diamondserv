"""
file: accounts/tests/test_models.py
author: lkmhaqer

Some simple tests to enforce our assumptions about model behaviour.
"""
from uuid import UUID

from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.models import InviteCode


def _is_valid_uuid(string):
  try:
    UUID(str(string))
    return True
  except ValueError:
    return False

class InviteCodeTests(TestCase):
  """ Simple invite code tests. """
  def setUp(self):
    self.invite = InviteCode(email='test@phukish.com')
    self.invite.save()

  def test_valid_invite_email(self):
    """ Test that we can create an invite with a valid email. """
    self.assertEqual(self.invite.email, 'test@phukish.com')

  def test_no_duplicate_email(self):
    """ Test that there cannot be duplicate email addresses. """
    with self.assertRaises(IntegrityError):
      invite_duplicate = InviteCode(email='test@phukish.com')
      invite_duplicate.save()

  def test_valid_uuid_created(self):
    """ Test that we get a valid uuid as a token when we create an invite. """
    self.assertEqual(_is_valid_uuid(self.invite.token), True)

  def test_invalid_uuid(self):
    """ Test that our uuid validator is working. """
    self.assertEqual(_is_valid_uuid('test'), False)
