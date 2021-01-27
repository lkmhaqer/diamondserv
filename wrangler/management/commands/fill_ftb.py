"""
file: utils/ftb_servertypes.py
author: lkmhaqer

Just a little utility to walk the FTB api and get the top ten modpacks.
"""
import json
import requests

from django.core.management.base import BaseCommand

from wrangler.models import EnvironmentVar, ServerType # pylint: disable=import-error


FTB_TOP_URL = 'https://api.modpacks.ch/public/modpack/popular/installs/FTB/20'
FTB_MODPACK_URL = 'https://api.modpacks.ch/public/modpack/'

class Command(BaseCommand):
  """
  We write our little utility as a Django subcommand. The command
  can be executed with `python manage.py fill_ftb` from the project
  root.
  """

  help = 'Fills the DB with server-types from the FTB API'

  def handle(self, *args, **options):
    response = requests.get(FTB_TOP_URL)
    query = json.loads(response.text)

    for i in query['packs']:
      response = requests.get(f'{FTB_MODPACK_URL}{i}')
      pack = json.loads(response.text)

      servertype, created = ServerType.objects.get_or_create(
        name=pack["name"],
        version=pack["versions"][-1]["name"],
        docker_image='itzg/minecraft-server:multiarch',
      )

      if created:
        ftb_type = EnvironmentVar.objects.get(name='TYPE', value='FTBA')
        mem_var = EnvironmentVar.objects.get(name='MEMORY', value='4G')
        ftb_mod, created = EnvironmentVar.objects.get_or_create(
          name='FTB_MODPACK_ID',
          value=i
        )
        ftb_mod_version, created = EnvironmentVar.objects.get_or_create(
          name='FTB_MODPACK_VERSION_ID',
          value=pack["versions"][-1]["id"]
        )
        servertype.environment_vars.add(mem_var.id, ftb_type.id, ftb_mod.id, ftb_mod_version.id)
        self.stdout.write(
          self.style.SUCCESS(
            f'Found {servertype}'
          )
        )
      else:
        self.stdout.write(
          self.style.WARNING(
            f'{servertype} already exists.'
          )
        )
