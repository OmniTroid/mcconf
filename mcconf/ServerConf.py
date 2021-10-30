import os
from pathlib import Path
import json
import requests
import subprocess
import time

from .SystemInterface import SystemInterface
from .exceptions import *

class ServerConf:
	def __init__(self, args : dict):
		import coreconf
		self.args = args
		self.coreconf = coreconf.coreconf
		self.system = SystemInterface()
		self.load_metaconf()
		self.serverdir = Path(args['serverdir']).resolve()
		self.start_path = Path(self.serverdir, 'start.sh')

	def load_metaconf(self):
		metaconf_path = Path(self.args['confdir'], 'metaconf.json')

		with open(metaconf_path) as file:
			self.metaconf = json.loads(file.read())

	def init_server(self):
		self.make_serverdir()
		self.write_eula()
		self.symlink_launcher()
		self.setup_plugins()
		self.make_start_script()

		print('Done! Now run the start script to generate the initial state')

		#self.generate_initial_state()

	def make_serverdir(self):
		print('### Make server directory')
		if self.serverdir.exists():
			print('INFO: ' + str(self.serverdir) + ' already exists, skipping mkdir step.')
		else:
			self.serverdir.mkdir()

	def write_eula(self):
		print('### Write eula file')

		eula_path = Path(self.serverdir, 'eula.txt')

		with open(eula_path, 'w') as file:
			file.write('eula=true\n')

	def symlink_launcher(self):
		print('### Symlink launcher')

		if 'launcher_version' in self.metaconf:
			version = self.metaconf['launcher_version']
		else:
			version = 'latest'

		launcher_src = Path(
			self.coreconf['launcher_dir'],
			self.metaconf['launcher'],
			version + '.jar'
		)

		if not launcher_src.exists():
			print('ERROR: ' + str(launcher_dst) + ' does not exist')
			raise FileNotFoundError

		launcher_dst = Path(self.serverdir, self.metaconf['name'] + '.jar')

		if launcher_dst.exists():
			print('INFO: ' + str(launcher_dst) + ' exists, skipping symlink step.')
		else:
			os.symlink(launcher_src, launcher_dst)

	def setup_plugins(self):
		print('### Setup plugins')
		server_plugin_dir = Path(self.serverdir, 'plugins')

		if not server_plugin_dir.exists():
			server_plugin_dir.mkdir()

		for plugin, plugin_conf in self.metaconf['plugins'].items():
			if 'version' in plugin_conf:
				version = plugin_conf['version']
			else:
				version = 'latest'

			plugin_src = Path(self.coreconf['plugin_dir'], plugin, version + '.jar')
			plugin_dst = Path(server_plugin_dir, plugin + '.jar')

			if not plugin_src.exists():
				print('WARNING: ' + str(plugin_src) + ' does not exist')

			if plugin_dst.exists():
				print('INFO: plugin symlink ' + str(plugin_dst) + ' exists, skipping.')
			else:
				os.symlink(plugin_src, plugin_dst)

	## Download and modify start script
	def make_start_script(self):
		print('### Make start script')

		if self.start_path.exists():
			print('# INFO: ' + str(self.start_path) + ' already exists. Skipping step.')

		response = requests.get(
			#'http://tiny.cc/mcstart',
			'https://gist.githubusercontent.com/OmniTroid/267730675631383ce3651155405b3474/raw/95bc84a677df065ebe032eeda5db5c2b72438d59/start.sh',
			headers={'User-Agent': 'mcconf'})

		if response.status_code != 200:
			raise ResponseInvalid

		start_script = response.text

		if 'java_version' in self.metaconf:
			java_version = self.metaconf['java_version']
		else:
			java_version = 'latest'

		java_path = Path(self.coreconf['java_dir'], java_version)

		if not java_path.exists():
			print('WARNING: ' + str(java_path) + ' does not exist')

		memory = str(self.metaconf['memory'])
		start_script = start_script.replace(
			'java', str(java_path)
		).replace(
			'paperclip.jar',
			self.metaconf['name'] + '.jar'
		).replace(
			'Xms10G',
			f'Xms{memory}G'
		).replace(
			'Xmx10G',
			f'Xmx{memory}G')

		self.start_path.write_text(start_script)

		# Make executable
		st = self.start_path.stat()
		self.start_path.chmod(st.st_mode | 0o111)

	## Start server and generate initial state
	def generate_initial_state(self):
		print('### Generate initial state')
		print(self.start_path)
		print('Starting server process')
		child_process = subprocess.Popen(
			self.start_path,
			stdin=subprocess.DEVNULL,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL)

		# Give it some time to set up
		print('Waiting 20 seconds...')
		time.sleep(20)

		# FIXME: child never responds to kill signal for some reason

		print('Killing server process')
		child_process.kill()

		print('Initial generation complete.')
