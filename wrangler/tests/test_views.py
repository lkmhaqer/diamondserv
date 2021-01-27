"""
file: wrangler/tests/test_views.py
author: lkmhaqer
"""
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from wrangler.models import MineHost, ServerType, Server


class TestViews(TestCase):
  """
  Our integration tests, testing requests end-to-end.
  """

  fake_logs = mock.MagicMock(
    return_value=b'These are the logs'
  )

  fake_delete = mock.MagicMock(
    return_value='Success!'
  )

  def setUp(self):
    self.user = User.objects.create_user('TestyMcTestFace', 'foo@bar.com', 'pw')
    self.test_user = User.objects.create_user('PrivateUser', 'ex@mple.com', 'pw')
    self.mine_host = MineHost(name='example.com')
    self.mine_host.save()
    self.server = Server(
      name='mc-test',
      owner=self.user,
      host=self.mine_host,
    )
    self.server.save()
    self.redirect_tests = [
      (
        ('wrangler:server_create', None),
        '/server/create'
      ),
      (
        ('wrangler:server_detail', {'server_name': 'mc-test'}),
        '/server/mc-test/detail'
      ),
      (
        ('wrangler:server_delete', {'server_name': 'mc-test'}),
        '/server/mc-test/delete'
      ),
    ]

  def test_anonymous_cannot_see_page(self):
    """ Test you cannot view the server create page if not logged in. """
    for test, expected in self.redirect_tests:
      with self.subTest():
        response = self.client.get(reverse(
          test[0], kwargs=test[1]
        ))

        self.assertRedirects(
          response,
          f'{settings.LOGIN_URL}?next={expected}',
        )

  def test_default_server_limit(self):
    """ Test that you can't exceed the max servers per user. """
    server_two = Server(
      name='mc-test2',
      owner=self.user,
      host=self.mine_host,
    )
    server_two.save()

    self.client.force_login(user=self.user)
    response = self.client.post(
      reverse('wrangler:server_create'),
      data={
        'name': 'mc-test3',
        'host': 1,
        'game_type': 0,
        'server_type': 1,
      }
    )

    self.assertFormError(
      response,
      'form',
      None,
      'You are only allowed 2 servers.'
    )

  def test_set_server_limit(self):
    """
    Test if we set the users server_limit, that the server_create
    form returns a "too many servers error" as expected.
    """

    self.user.server_limit = 1
    self.user.save()

    self.client.force_login(user=self.user)
    response = self.client.post(
      reverse('wrangler:server_create'),
      data={
        'name': 'mc-test4',
        'host': 1,
        'game_type': 0,
        'server_type': 1,
      }
    )

    self.assertFormError(
      response,
      'form',
      None,
      'You are only allowed 1 servers.'
    )

  @mock.patch('wrangler.views.docker_get_logs', fake_logs)
  def test_server_detail_logs_only_viewed_by_owner(self):
    """
    Test that we return 403 if the server owner
    is not the logged in user.
    """
    private_server = Server(
      name='private-mc',
      owner=self.test_user,
      host=self.mine_host,
    )
    private_server.save()

    self.client.force_login(user=self.user)
    response = self.client.get(reverse(
      'wrangler:server_detail',
      kwargs={'server_name': 'private-mc'},
    ))

    self.assertNotContains(response, 'These are the logs')

  @mock.patch('wrangler.views.docker_get_logs', fake_logs)
  def test_server_detail_logs_can_be_viewed(self):
    """ Test that the owner can view the detail page. """

    self.client.force_login(user=self.user)
    response = self.client.get(reverse(
      'wrangler:server_detail',
      kwargs={'server_name': 'mc-test'},
    ))

    self.assertContains(response, 'These are the logs')

  def test_mine_host_not_offered_when_disabled(self):
    """ Test that a mine_host is not in the form when it's disabled. """

    disabled_host = MineHost(name='disabled.example.com', enabled=False)
    disabled_host.save()

    self.client.force_login(user=self.user)
    response = self.client.get(reverse('wrangler:server_create'))

    self.assertNotContains(response, 'disabled.example.com')

  def test_server_type_not_offered_when_disabled(self):
    """ Test that a server_type is not in the form when it's disabled. """

    disabled_type = ServerType(
      name='ExampleMod',
      enabled=False,
      version='1.0.0',
      docker_image='a-minecraft-docker-image',
    )
    disabled_type.save()

    self.client.force_login(user=self.user)
    response = self.client.get(reverse('wrangler:server_create'))

    self.assertNotContains(response, 'ExampleMod')

  @mock.patch('wrangler.views.docker_delete_server', fake_delete)
  def test_server_delete_page_only_triggered_by_owner(self):
    """
    Test that we return 403 if the server owner
    is not the logged in user.
    """

    self.client.force_login(user=self.test_user)
    response = self.client.post(reverse(
      'wrangler:server_delete',
      kwargs={'server_name': 'mc-test'},
    ))

    self.assertEqual(response.status_code, 403)

  @mock.patch('wrangler.views.docker_restart_server', fake_delete)
  def test_server_restart_page_only_triggered_by_owner(self):
    """
    Test that we return 403 if the server owner
    is not the logged in user.
    """

    self.client.force_login(user=self.test_user)
    response = self.client.post(reverse(
      'wrangler:server_restart',
      kwargs={'server_name': 'mc-test'},
    ))

    self.assertEqual(response.status_code, 403)

  def test_only_request_user_can_see_user_status(self):
    """
    Test that we return 403 if the logged in user
    doesn't match the user making the user_status request.
    """

    self.client.force_login(user=self.user)
    response = self.client.get(reverse(
      'wrangler:user_status',
      kwargs={'username': 'PrivateUser'},
    ))

    self.assertEqual(response.status_code, 403)

  def test_that_a_host_is_not_listed_when_full(self):
    """
    Test that when we go to create a server, only hosts that are not full,
    are presented. A host is "not full" when it has less servers than it's
    server_limit.
    """

    self.mine_host.server_limit = 1
    self.mine_host.save()

    self.client.force_login(user=self.user)
    response = self.client.get(reverse('wrangler:server_create'))

    self.assertNotContains(response, 'example.com')

  def test_that_a_host_is_listed_when_not_full(self):
    """
    Test that when we go to create a server, non-full hosts are presented
    """

    self.mine_host.server_limit = 7
    self.mine_host.save()

    self.client.force_login(user=self.user)
    response = self.client.get(reverse('wrangler:server_create'))

    self.assertContains(response, 'example.com')
