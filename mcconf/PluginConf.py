import os
import sys

#import mcconf.webfunctions as webfunctions
from .Provider import Provider
from .Spiget import Spiget
from .Bukkit import Bukkit
from .exceptions import *

class PluginConf:
	def __init__(self, config : dict):
		self.config = config

# Entry point from command line

	def start(self):
		if len(sys.argv) < 2:
			self.print_help()
			exit()

		command = sys.argv[1]

		if command == 'list':
			self.list_resources()
		elif command == 'download':
			if len(sys.argv) < 3:
				raise ArgumentMissing('resource_name')

			resource_name = sys.argv[2]
			resource_version = 'latest'

			if len(sys.argv) > 3:
				resource_version = sys.argv[3]

			self.download_resource(resource_name, resource_version)
		else:
			raise CommandUnknown(command)

### Utility functions, getters

	def print_help(self):
		print('''
pluginconf command [args..]

Commands:

- download resource_name [resource_version]
	Downloads latest version of given resource name.
	If a version is not specified, download latest.
	ex: pluginconf download EssentialsX

- update resource_name
	Downloads latest version of given resource name and updates symlink
	ex: pluginconf update EssentialsX

- list
	Lists configured resources (plugins)
''')

	def get_resources(self) -> dict:
		return self.config['resources']

	def list_resources(self):
		for key, value in self.get_resources().items():
			print(key)

	def resource_name_from_id(self, resource_id : str) -> str:
		for key, value in self.config['resources']:
			if value['id'] == resource_id:
				return key

		return ''

	def get_provider(self, provider_name : str) -> Provider:
		if provider_name == 'spiget':
			return Spiget()
		elif provider_name == 'bukkit':
			return Bukkit()
		else:
			raise ProviderNotConfigured
### Other

	# Downloads the resource with specified name and version
	def download_resource(self, resource_name : str, resource_version : str = 'latest'):
		if resource_name not in self.config['resources']:
			raise ResourceNotConfigured(resource_name)

		provider_name = self.config['resources'][resource_name]['provider']
		provider = self.get_provider(provider_name)
		resource_id = self.config['resources'][resource_name]['id']

		if resource_version == 'latest':
			version_number, version_id = provider.get_latest_version_data(resource_id)
		else:
			version_number = resource_version
			version_id = provider.get_version_id(resource_id, version_number)

		provider.request_resource_download(resource_id, version_id)

		#if download_response == None:
		#	return

		#filetype = ''

		#if headers['Content-Type'] == 'application/zip':
		#	filetype = 'zip'
		#else:
		#	print('Unknown Content-Type: ' + headers['Content-Type'])
		#	return

		#if not path.exists(resource_name):
		#	os.mkdir(resource_name)

		#os.chdir(resource_name)

		#filename = f'{filename}.{filetype}'

		#outfile = open(filename, 'wb')
		#outfile.write(response.content)
		#outfile.close()

		#if resource_filetype == 'zip':
		#	pass


		#os.chdir(cwd)
