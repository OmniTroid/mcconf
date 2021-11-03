import configparser
from pathlib import Path
import io
from typing import Callable
import yaml

import dictcombiner.dictcombiner as dc

class UpdateConf:
	def __init__(self, args):
		self.args = args
		self.confdir = Path(args['confdir'])
		self.serverdir = Path(args['serverdir'])

		if not self.confdir.exists():
			print('ERROR: ' + confdir + ' does not exist')
			return

		if not self.serverdir.exists():
			print('ERROR: ' + serverdir + ' does not exist')
			return

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

		subconfs = []

		for subconf_file in subconf_files:
			subconfs.append(read_func(subconf_file))

		result_conf = dc.combine_dicts(baseconf, subconfs)

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

