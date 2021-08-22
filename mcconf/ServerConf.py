import os
from pathlib import Path
import json
import requests
import subprocess
import time

import coreconf

from .SystemInterface import SystemInterface
from .exceptions import *

class ServerConf:
	def __init__(self, args : dict):
		self.args = args
		self.coreconf = coreconf.coreconf
		self.system = SystemInterface()
		self.load_metaconf()
		self.server_path = Path(args['outdir'], self.metaconf['name']).resolve()
		self.start_path = Path(self.server_path, 'start.sh').resolve()

	def load_metaconf(self):
		metaconf_path = Path(self.args['confdir'], 'metaconf.json')

		with open(metaconf_path) as file:
			self.metaconf = json.loads(file.read())

	def init_server(self):
		if self.server_path.exists():
			raise FileExistsError(self.server_path)

		## Make directory
		print('### Make server directory')
		self.server_path.mkdir()
		os.chdir(self.server_path)

		## Symlink launcher
		print('### Symlink launcher')
		launcher_path = Path(
			self.coreconf['launcher_dir'],
			self.metaconf['launcher'],
			self.metaconf['launcher_version'] + '.jar'
		)

		os.symlink(launcher_path, self.metaconf['name'] + '.jar')

		## Write eula file
		print('### Write eula file')
		with open('eula.txt', 'w') as eula_file:
			eula_file.write('eula=true\n')

		self.make_start_script()
		self.generate_initial_state()

	## Download and modify start script
	def make_start_script(self):
		response = requests.get(
			#'http://tiny.cc/mcstart',
			'https://gist.githubusercontent.com/OmniTroid/267730675631383ce3651155405b3474/raw/95bc84a677df065ebe032eeda5db5c2b72438d59/start.sh',
			headers={'User-Agent': 'mcconf'})

		if response.status_code != 200:
			raise ResponseInvalid

		start_script = response.text

		memory = str(self.metaconf['memory'])
		start_script = start_script.replace(
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

		print('Killing server process')
		child_process.kill()

		print('Initial generation complete.')

	# Links the relevant launcher and plugins and generates initial state.



	def init_plugins(self):
		pass

