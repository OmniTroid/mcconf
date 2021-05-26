import requests

import mcconf.webfunctions as webfunctions
from .Provider import Provider

class Spiget(Provider):
	def __init__(self):
		self.api_url = 'https://api.spiget.org/v2/resources/'
		self.download_url = self.api_url + '{resource_id}/versions/{resource_version_id}/download'

	# Sends a request to download from given provider given resource with specific version id
	# Returns a response object
	def get_latest_version_data(self, resource_id : str) -> [str, str]:
		url = self.api_url + f'{resource_id}/versions/latest'

		response = webfunctions.request(url)

		version_number = response.json()['name']
		version_id = str(response.json()['id'])

		return [version_number, version_id]

	# Return the filetype of the given resource id
	def get_resource_filetype(self, resource_id : str) -> str:
		pass

	# Gets the latest version number and version id of a given resource
	def request_resource_download(self, resource_id : str, resource_version_id : str) -> requests.Response:
		url = self.download_url.format(resource_id = resource_id, resource_version_id = resource_version_id)ß

		return webfunctions.request(url)
