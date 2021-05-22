import requests
#import config as c
import os

class PluginConf:
	def __init__(self, config : dict):
		self.config = config

	def get_resources(self) -> dict:
		return self.config['resources']

	def make_request(self, url : str, expected_status_code = 200) -> requests.Response:
		headers = {'User-Agent': 'mcconf plugin updater'}

		response = requests.get(url, headers = headers)

		if response.status_code != expected_status_code:
			print('Web request failed: ' + url)
			print('Expected code: ' + str(expected_status_code))
			print('Received code: ' + str(response.status_code))
			return None

		return response

	# Gets data about the latest version of a given resource id
	# As a dictionary
	# Dictionary is empty on failure
	def spiget_latest_version_data(self, resource_id : str) -> dict:
		url = self.config['providers']['spiget']['latest_version_data_url']
		response = self.make_request(url.format(resource_id = resource_id))
		if response == None:
			return {}

		return response.json()

	# Downloads specified resource to current directory
	def download_resource(self, resource_name : str):
		cwd = os.getcwd()
		os.chdir(c.plugin_dir)
		resource_id = resource_metadata[resource_name]['id']
		resource_filetype = resource_metadata[resource_name]['filetype']



		filename = f'{resource_name}-{resource_version}.{resource_filetype}'

		if os.path.exists(filename):
			print('File already exists: ' + os.getcwd() + filename)
			return

		download_response = make_request(download_url.format(
			resource_id = resource_id,
			resource_version_id = resource_version_id))

		if download_response == None:
			return

		filetype = ''

		if headers['Content-Type'] == 'application/zip':
			filetype = 'zip'
		else:
			print('Unknown Content-Type: ' + headers['Content-Type'])
			return

		if not path.exists(resource_name):
			os.mkdir(resource_name)

		os.chdir(resource_name)

		filename = f'{filename}.{filetype}'

		outfile = open(filename, 'wb')
		outfile.write(response.content)
		outfile.close()

		if resource_filetype == 'zip':
			pass


		os.chdir(cwd)
