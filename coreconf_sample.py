coreconf = {
	'java_dir': '/data/java',
	'plugin_dir': '/data/mc/plugins',
	'launcher_dir': '/data/mc/launchers',
	'roles_dir': '/data/mc/mc.buk.gg-conf/roles',

	'resources': {
		'EssentialsX': {'id': '9089', 'filetype': 'zip', 'provider': 'spiget'},
		'TownyAdvanced': {'id': '72694', 'filetype': 'zip', 'provider': 'spiget'},
		'LuckPerms': {'id': '28140', 'filetype': 'jar', 'provider': 'spiget'},
		'Vault': {'id': '34315', 'filetype': 'jar', 'provider': 'spiget'},
		'WorldEdit': {'id': 'worldedit', 'filetype': 'jar', 'provider': 'bukkit'},
		'WorldBorder': {'id': '60905', 'filetype': 'jar', 'provider': 'spiget'},
		'WorldGuard': {'id': 'worldguard', 'filetype': 'jar', 'provider': 'bukkit'}
	},

	'providers': {
		'spiget': {
			'download_url': 'https://api.spiget.org/v2/resources/{resource_id}/versions/{resource_version_id}/download',
			'latest_version_data_url': 'https://api.spiget.org/v2/resources/{resource_id}/versions/latest'
		},
		'bukkit': {
			'download_url': 'https://dev.bukkit.org/projects/{resource_id}/files/{resource_version_id}/download'
		}
	}
}
