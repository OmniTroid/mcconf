import io
import yaml
import json
import configparser
import pprint
from pathlib import Path
from typing import Callable

import dictcombiner.dictcombiner as dc
import fs2conf as fc

class UpdateConf:
	def __init__(self, args):
		self.args = args
		self.serverconf = Path(args['serverconf'])
		self.rolesdir = Path(args['rolesdir'])
		self.serverdir = Path(args['serverdir'])
		self.conf = {}
		self.metaconf = {}
		self.action = args['action']

		if not self.serverconf.is_file():
			print('ERROR: ' + confdir + ' does not exist')
			raise FileNotFoundError

		if not self.rolesdir.is_dir():
			print('ERROR: ' + self.rolesdir + ' does not exist')
			raise NotADirectoryError

		if not self.serverdir.exists() and self.action != 'init':
			print('ERROR: ' + self.serverdir + ' does not exist')
			raise NotADirectoryError

		roledirs = [
			Path(self.rolesdir, role) for role in 
				json.loads(open(self.serverconf).read())['roles']
		]

		self.combined_conf = fc.combine_dirs(roledirs)

		pprint.pprint(self.combined_conf)

		self.metaconf = self.combined_conf['metaconf.json']
		self.conf = self.combined_conf['conf']

	def init_server(self):
		self.make_serverdir()
		self.write_eula()
		self.symlink_launcher()
		self.setup_plugins()
		self.make_start_script()

		print('Done! Now run the start script to generate the initial state')

## initserver functions

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

### Update functions

	def update_all(self):
		self.update_server_properties()
		self.update_bukkit_yml()
		self.update_spigot_yml()
		self.update_paper_yml()
		#self.update_plugin_confs()

	def update_server_properties(self):
		baseconf_path = Path(self.serverdir, 'server.properties')
		subconf_dir = Path(self.confdir, 'server.properties')
		self.update_conf(
			baseconf_path, subconf_dir,
			self.read_properties_file, self.write_properties_file)

	def update_bukkit_yml(self):
		self.update_core_yml('bukkit')

	def update_spigot_yml(self):
		self.update_core_yml('spigot')

	def update_paper_yml(self):
		self.update_core_yml('paper')

	def update_plugin_confs(self):
		plugins_conf_dir = Path(self.confdir, 'plugins')

		if not plugins_conf_dir.exists():
			print('INFO: ' + str(plugins_conf_dir) + ' not found, skipping')
			return

		for dir_ in plugins_conf_dir.iterdir():
			conf_dir = Path(dir_)
			# This is where we will add exceptions for plugins that dont have config.yml
			conf_name = 'config.yml'
			baseconf_path = Path(self.serverdir, 'plugins', conf_dir.name, 'config.yml')

	# Wrapper for updating core yml files (bukkit.yml, spigot.yml etc.)
	def update_core_yml(self, name : str):
		core_yml_path = Path(self.serverdir, name + '.yml')
		sub_yml_dir = Path(self.confdir, name + '.yml')

		self.update_conf(
			core_yml_path, sub_yml_dir,
			self.read_yml, self.write_yml)

	def update_conf(self,
			baseconf_path : Path, subconf_dir : Path,
			read_func : Callable, write_func : Callable):

		if not baseconf_path.exists():
			print('ERROR: ' + str(baseconf_path) + ' not found.')
			return

		# This means the file has no config, which is perfectly valid
		if not subconf_dir.exists():
			print('INFO: ' + str(subconf_dir) + ' not found, skipping.')
			return

		original_path = Path(baseconf_path.parent, 'original_' + baseconf_path.name)

		# Use the original file if we have it
		# This means the script has been run before
		# This ensures idempotency
		if original_path.exists():
			baseconf = read_func(original_path)
		else:
			baseconf = read_func(baseconf_path)

		subconf_files = sorted(
			[Path(filename) for filename in subconf_dir.iterdir()],
			key=lambda f: f.name)

		confs = [baseconf]

		for subconf_file in subconf_files:
			confs.append(read_func(subconf_file))

		result_conf = dc.combine_dicts(confs)

		if not original_path.exists():
			baseconf_path.rename(original_path)

		write_func(baseconf_path, result_conf)

### Read and write helpers
	def read_properties_file(self, path : Path) -> dict:
		## HACK: so server.properties actually lacks the section header.
		## configparse doesn't like this so we have to hack around that.
		conf_str = '[default]\n'

		with open(path) as file:
			data = file.read()
			conf_str = conf_str + data

			tmp_conf = configparser.ConfigParser()
			tmp_conf.read_string(conf_str)

			conf = dict(tmp_conf.items('default'))

			return conf

	def write_properties_file(self, path : Path, data : dict):
		with open(path, 'w') as file:
			tmp_dict = {'default': data}
			tmp_conf = configparser.ConfigParser()
			tmp_conf.read_dict(tmp_dict)
			tmp_conf.write(file)

	def read_yml(self, path : Path) -> dict:
		with open(path) as file:
			data = yaml.safe_load(file)

		return data

	def write_yml(self, path : Path, data : dict):
		with open(path, 'w') as file:
			file.write(yaml.dump(data))
