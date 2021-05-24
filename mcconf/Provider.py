import requests

from .exceptions import FunctionNotImplemented

class Provider:
	def get_latest_version_data(self, resource_name : str) -> [str, str]:
		raise FunctionNotImplemented
	def request_resource_download(self, resource_id : str, resource_version_id : str) -> requests.Response:
		raise FunctionNotImplemented

