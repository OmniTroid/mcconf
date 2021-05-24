import requests

from .exceptions import ResponseInvalid

# Basic wrapper for web requests
def request(url : str, http_method : str = 'GET', expected_status_code : int = 200) -> requests.Response:
	headers = {'User-Agent': 'mcconf (https://github.com/OmniTroid/mcconf)'}

	response = requests.request(http_method, url, headers = headers)

	if response.status_code != expected_status_code:
		print('Web request failed: ' + url)
		print('Expected code: ' + str(expected_status_code))
		print('Received code: ' + str(response.status_code))

		raise ResponseInvalid(str(response.status_code))

	return response