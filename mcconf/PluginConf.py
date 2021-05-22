import requests
import os

class PluginConf:
	def __init__(self, config : dict):
		self.config = config

### Utility functions, getters

	def get_resources(self) -> dict:
		return self.config['resources']

	def resource_name_from_id(self, resource_id : str) -> str:
		for key, value in self.config['resources']:
			if value['id'] == resource_id:
				return key

		return ''

### Request functions, returning a requests.Response object

	# Basic wrapper for web requests
	def request(self, url : str, expected_status_code : int = 200) -> requests.Response:
		headers = {'User-Agent': 'mcconf plugin updater'}

		response = requests.get(url, headers = headers)

		if response.status_code != expected_status_code:
			print('Web request failed: ' + url)
			print('Expected code: ' + str(expected_status_code))
			print('Received code: ' + str(response.status_code))

		return response

	# Sends a request to download from given provider given resource with specific version id
	# Returns a response object
	def request_resource_download(self, provider : str, resource_id : str, resource_version_id : str) -> requests.Response:
		#cwd = os.getcwd()
		#os.chdir(self.config['plugin_dir'])

		#filename = f'{resource_name}-{resource_version}.{resource_filetype}'

		#if os.path.exists(filename):
		#	print('File already exists: ' + os.getcwd() + filename)
		#	return

		url = self.config[provider]['download_url'].format(
			resource_id = resource_id,
			resource_version_id = resource_version_id)

		return make_request(url)

	# Sends a request to get the latest version data of a given resource id from a given provider
	# Returns a response object
	def request_latest_version_data(self, provider : str, resource_id : str) -> requests.Response:
		url = self.config['providers'][provider]['latest_version_data_url'].format(resource_id = resource_id)

		return self.make_request(url.format(resource_id = resource_id))

### Other

	def download_resource(self):
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
