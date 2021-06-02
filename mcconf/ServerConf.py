import os

from .SystemInterface import SystemInterface
from .exceptions import *

class ServerConf:
	def __init__(self, config : dict, recipe : dict):
		self.config = config
		self.recipe = recipe
		self.system = SystemInterface()

	def init_plugins(self):
		pass

	# Links the relevant launcher and plugins and generates initial state.
	def init_server(self, server_name : str, dry_run=False, verbosity=0):
		self.system.dry_run = dry_run
		self.system.verbosity = verbosity

		server_path = os.path.join(self.config['server_dir'], server_name)

		if os.path.exists(server_path):
			raise ServerExists(server_name)

		self.system.makedirs(server_path)
		os.chdir(server_path)

		os.symlink(self.recipe['launcher'], self.recipe['name'] + '.jar')

		eula_file = open('eula.txt', 'w')
		eula_file.write('eula=true\n')
		eula_file.close()

