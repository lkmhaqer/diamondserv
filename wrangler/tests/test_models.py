"""
file: wrangler/tests/test_models.py
author: lkmhaqer
"""
from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.models import User

from wrangler.models import MineHost, Server


class MineHostTests(TestCase):
  """ Tests for the MineHost Model """
  def setUp(self):
    self.mine_host = MineHost(name='minecraft-00.cvn')
    self.mine_host.save()

  def test_valid_mine_host_and_str(self):
    """ Test that we can save a valid MC host name. """
    self.assertEqual(self.mine_host.name, 'minecraft-00.cvn')

  def test_no_duplicate_mine_host_names(self):
    """ Test that we cannot save a duplicate name. """
    with self.assertRaises(IntegrityError):
      mine_host_duplicate = MineHost(name='minecraft-00.cvn')
      mine_host_duplicate.save()


class ServerTests(TestCase):
  """
  Tests for the Server Model
  In setup, we create four servers to help test port assignment is working.
  Servers are all named similar, and the third server (2 from 0 index)
  is separated out, with it's port number being custom defined for it's test.
  """
  def setUp(self):
    self.user = User(username='test', password='testfest', email='foo@bar.com')
    self.user.save()
    self.mine_host = MineHost(name='minecraft-00.cvn')
    self.mine_host.save()
    self.servers = []
    for i in range(0, 4):
      if i == 2:
        server = Server(
          name=f'mc-0{i}',
          owner=self.user,
          host=self.mine_host,
          port=25570
        )
      else:
        server = Server(name=f'mc-0{i}', owner=self.user, host=self.mine_host)

      server.save()
      self.servers.append(server)

  def test_valid_mc_server(self):
    """ Test that we can save a valid MC server name. """
    self.assertEqual(self.servers[0].name, 'mc-00')

  def test_no_duplicate_server_names(self):
    """ Test that we cannot save a duplicate name. """
    with self.assertRaises(IntegrityError):
      server_duplicate = Server(
        name='mc-00',
        owner=self.user,
        host=self.mine_host
      )
      server_duplicate.save()

  def test_server_port_find_one_server(self):
    """
    We want to test that when a server is created, if no port is specified,
    that we select the "next available" port number that will be unique to
    the host the server is on, from a default range of 25565 to 25693.

    This means the first server should be 25565, the second 25566. Then if
    we manually create a third server with port 25570, a fourth server
    should autopick 25567.

    The port assignment should be happening on the initial
    Server.save() only, and servers are defined above in setUp().
    """
    self.assertEqual(self.servers[0].port, self.mine_host.min_port)

  def test_server_port_find_two_server(self):
    """ Test two servers can find ports. """
    self.assertEqual(self.servers[1].port, self.mine_host.min_port + 1)

  def test_server_port_find_three_server_custom_port(self):
    """ Test that we can define our own port number if we want. """
    self.assertEqual(self.servers[2].port, 25570)

  def test_server_port_find_four_server(self):
    """
    Test that our fourth server picks the next availble port,
    not a port that is just the highest plus one.
    """
    self.assertEqual(self.servers[3].port, self.mine_host.min_port + 2)
