import requests

from .exceptions import FunctionNotImplemented

class Provider:
	# Get the latest version data from given resource name
	def get_latest_version_data(self, resource_name : str) -> [str, str]:
		raise FunctionNotImplemented
	# Get the version id given the resource name and version name
	def get_version_id(self, resource_name : str, version_name : str) -> str:
		raise FunctionNotImplemented
	# Sends a web request to download resource with given resource id and version id
	def request_resource_download(self, resource_id : str, resource_version_id : str) -> requests.Response:
		raise FunctionNotImplemented

