"""
file: wrangler/tasks.py
author: lkmhaqer

This is our background tasks file, we have several actions that should
be triggered from the UI, but executed without stopping our web application.
"""
from socket import gaierror

from mcstatus import MinecraftServer

from docker import DockerClient
from docker.errors import DockerException


def _get_client(server):
  """Return a TCP based network client to docker

  Args:
      server (SerializedServer): A JSON object of our Server model

  Returns:
      DockerClient: An instance of a client from docker-py
  """
  return DockerClient(base_url=f"tcp://{server.host.name}:2375")

def docker_get_logs(server):
  """Get logs from a docker server

  Args:
      server (Server): An object of our Server model

  Returns:
      list: A list of the log lines from docker
  """
  try:
    client = _get_client(server)
    container = client.containers.get(server.name)
    return container.logs(tail=50)
  except DockerException:
    return b'Unable to collect logs.'

def docker_restart_server(server):
  """Restart a docker server

  Args:
      server (Server): An object of our Server model
  """
  try:
    client = _get_client(server)
    container = client.containers.get(server.name)
    container.restart()
    return 'Success!'
  except DockerException:
    return 'Error restarting this server.'

def docker_start_server(server):
  """Start a docker server

  Args:
      server (Server): An object of our Server model
  """
  client = _get_client(server)
  op_list = ','.join(server.op_list.values_list('name', flat=True))
  mod_volume = None
  env = [
    'EULA=TRUE',
    f"OPS=lkmhaqer,{op_list}",
    f"MOTD=Phukish Minecraft {server.name} ({server.server_type.name})",
    f"MODE={server.game_type}"
  ]
  for var in list(server.server_type.environment_vars.values()):
    env.append(f"{var['name']}={var['value']}")
    if var['name'] == 'CF_SERVER_MOD':
      mod_volume = {'/srv/modpacks': {'bind': '/modpacks', 'mode': 'ro'}}

  client.containers.run(
    image=server.server_type.docker_image,
    name=server.name,
    ports={'25565/tcp': server.port},
    detach=True,
    restart_policy={'Name': 'always', 'MaximumRetryCount': 0},
    environment=env,
    volumes=mod_volume,
  )

def docker_delete_server(server):
  """Hit the minecraft host with a docker stop and rm

  Args:
      server (Server): An JSON object of our Server model
  """
  client = _get_client(server)
  container = client.containers.get(server.name)
  container.remove(force=True)

def minecraft_status(server_list):
  """Check a list of servers for their current minecraft server status.

  Args:
      server_list ([Server()]): A list of Server() objects.

  Returns:
      dict: returns a dictionary of information about the list of servers.
  """
  servers = []
  total_players = 0
  total_capacity = 0
  for server in server_list:
    query = MinecraftServer.lookup(server.get_socket())
    try:
      servers.append((server, query.status()))
      total_players += query.status().players.online
      total_capacity += query.status().players.max
    except (
      BrokenPipeError,
      ConnectionRefusedError,
      ConnectionResetError,
      gaierror,
      OSError
    ) as err:
      down_status = {'version': {'text': '', 'error': err} }
      servers.append((server, down_status))

  output = {
    'serverlist': servers,
    'total_players': total_players,
    'total_capacity': total_capacity
  }

  return output
