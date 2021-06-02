import os

class ServerConf:
	def __init__(self, config : dict):
		self.config = config

	# Links the relevant launcher and plugins and generates initial state.
	def init_server(world_name : str):
		os.makedirs(config.server_dir, exist_ok=)

		os.mkdir(world_name)
		os.chdir(world_name)
