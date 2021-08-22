import os
from pathlib import Path
import json
import requests
import subprocess

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

	def load_metaconf(self):
		metaconf_path = Path(self.args['confdir'], 'metaconf.json')

		with open(metaconf_path) as file:
			self.metaconf = json.loads(file.read())

	# Links the relevant launcher and plugins and generates initial state.
	def init_server(self):
		if self.server_path.exists():
			raise FileExistsError(self.server_path)

		## Make directory
		self.server_path.mkdir()
		os.chdir(self.server_path)

		## Symlink launcher
		launcher_path = Path(
			self.coreconf['launcher_dir'],
			self.metaconf['launcher'],
			self.metaconf['launcher_version'] + '.jar'
		)

		os.symlink(launcher_path, self.metaconf['name'] + '.jar')

		## Write eula file
		with open('eula.txt', 'w') as eula_file:
			eula_file.write('eula=true\n')

		## Download start script
		response = requests.get(
			#'http://tiny.cc/mcstart',
			'https://gist.githubusercontent.com/OmniTroid/267730675631383ce3651155405b3474/raw/95bc84a677df065ebe032eeda5db5c2b72438d59/start.sh',
			headers={'User-Agent': 'mcconf'})

		if response.status_code != 200:
			raise ResponseInvalid

		start_script = response.text
		start_path = Path('start.sh').resolve()

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

		start_path.write_text(start_script)

		# Make executable
		st = start_path.stat()
		start_path.chmod(st.st_mode | 0o111)

		## Start server and generate initial state
		subprocess.run(start_path, capture_output=True)

		# TODO: add a reasonable timer here


	def init_plugins(self):
		pass

