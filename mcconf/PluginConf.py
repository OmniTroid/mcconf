import requests
import os
import sys

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

### Request functions, returning a requests.Response object

	# Basic wrapper for web requests
	def request(self, url : str, http_method : str = 'GET', expected_status_code : int = 200) -> requests.Response:
		headers = {'User-Agent': 'mcconf plugin updater'}

		response = requests.request(http_method, url, headers = headers)

		if response.status_code != expected_status_code:
			print('Web request failed: ' + url)
			print('Expected code: ' + str(expected_status_code))
			print('Received code: ' + str(response.status_code))

			raise ResponseInvalid(str(response.status_code))

		return response

	# Sends a request to download from given provider given resource with specific version id
	# Returns a response object
	def request_resource_download(self, provider : str, resource_id : str, resource_version_id : str) -> requests.Response:
		url = self.config[provider]['download_url'].format(
			resource_id = resource_id,
			resource_version_id = resource_version_id)

		return make_request(url)

	# Sends a request to get the latest version data of a given resource id from a given provider
	# Returns a response object
	def request_latest_version_data(self, provider : str, resource_name : str) -> requests.Response:
		resource_id = self.config['resources'][resource_name]['id']
		url = self.config['providers'][provider]['latest_version_data_url'].format(resource_id = resource_id)

		return self.request(url.format(resource_id = resource_id))

	# Gets the latest version number and version id of a given resource
	def get_latest_version_data(self, resource_name : str) -> [str, str]:
		provider = self.config['resources'][resource_name]['provider']

		if provider == 'spiget':
			response = self.request_latest_version_data(provider, resource_name)

			version_number = response.json()['name']
			version_id = str(response.json()['id'])
		elif provider == 'bukkit':
			# For bukkit, we need to GET the webpage with the list of versions
			# then parse the results, TODO
			raise FunctionalityNotImplemented('get_latest_version_data for bukkit')
		else:
			raise ProviderNotConfigured(provider)

		return [version_number, version_id]

### Other

	# Downloads the resource with specified name and version
	def download_resource(self, resource_name : str, resource_version : str = 'latest'):
		if resource_name not in self.config['resources']:
			raise ResourceNotConfigured(resource_name)

		provider = self.config['resources'][resource_name]['provider']
		#resource_id = self.config['resources'][resource_name]['id']

		if resource_version == 'latest':
			version_number, version_id = self.get_latest_version_data(resource_name)
		else:
			# TODO: implement downloading specific version
			pass

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
