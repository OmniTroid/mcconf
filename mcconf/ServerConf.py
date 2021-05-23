import os
import config as c

# Links the relevant launcher and plugins and generates initial state.
def init_world(world_name : str, launcher_path : str):
	os.mkdir(world_name)
	os.chdir(world_name)


if __name__ == '__main__':
	init_world('test')