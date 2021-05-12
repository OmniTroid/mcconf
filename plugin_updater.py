import requests
import config as c
import os

api_url = 'https://api.spiget.org/v2/resources/{resource_id}'
version_url = api_url + '/versions/latest'
download_url = api_url + '/versions/{resource_version_id}/download'

resource_metadata = {
	'EssentialsX': {'id': '9089', 'filetype': 'zip'}
}

valid_filetypes = {
	'zip',
	'jar'
}

def make_request(url : str, expected_status_code = 200) -> requests.Response:
	headers = {'User-Agent': 'mcconf plugin updater'}

	response = requests.get(url, headers = headers)

	if response.status_code != expected_status_code:
		print('Web request failed: ' + url)
		print('Expected code: ' + str(expected_status_code))
		print('Received code: ' + str(response.status_code))
		return None

	return response

# Downloads specified resource to current directory
def download_resource(resource_name : str):
	cwd = os.getcwd()
	os.chdir(c.plugin_dir)
	resource_id = resource_metadata[resource_name]['id']

	# Get data about the latest version
	version_response = make_request(version_url.format(resource_id = resource_id))
	if version_response == None:
		return

	version_response_json = version_response.json()
	resource_version = version_response_json['name']
	resource_version_id = version_response_json['id']

	filename = f'{resource_name}-{resource_version}'

	# Check if we have the exact version already
	for filetype in valid_filetypes:
		if os.path.exists(filename + '.' + filetype):
			print('File already exists: ' + os.getcwd() + filename + '.' + filetype)
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

	#if filetype == 'zip'



	os.chdir(cwd)

download_resource('EssentialsX')