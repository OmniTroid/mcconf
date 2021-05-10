import requests
import config as c

api_url = 'https://api.spiget.org/v2/resources/{resource_id}'
version_url = api_url + '/versions/latest'
download_url = api_url + '/download'

resource_ids = {
	'EssentialsX': '9089'
}

# Downloads specified resource to current directory
def download_resource(resource_name : str):
	cwd = os.getcwd()
	os.chdir(c.plugin_dir)
	resource_id = resource_ids[resource_name]

	headers = {'User-Agent': 'mcconf plugin updater'}

	version_response = requests.get(version_url.format(resource_id = resource_id), headers=headers)

	response = requests.get(api_url.format(resource_id = resource_id), headers=headers)

	print(response.headers)

	if response.status_code != 200:
		print('Failed to download resource ' + resource_name)
		return

	filetype = ''

	if headers['Content-Type'] == 'application/zip':
		filetype = 'zip'
	else
		print('Unknown Content-Type: ' + headers['Content-Type'])
		return

	outfile = open(filename + '.' + filetype, 'wb')
	outfile.write(response.content)
	outfile.close()




	os.chdir(cwd)

download_resource('EssentialsX')