import os
from typing import Callable

class SystemInterface():
	def __init__(self, dry_run=False, verbosity=0):
		self.dry_run = dry_run
		self.verbosity = verbosity

	def run(self, command : str):
		if self.verbosity >= 2:
			print(command)

		if not self.dry_run:
			os.system(command)

	def cd(self, dir_ : str):
		if self.verbosity >= 2:
			print('cd ' + dir_)

		if not self.dry_run:
			os.chdir(dir_)

	def makedirs(self, *args):
		if self.verbosity >= 2:
			print('mkdir ' + args[0])

		if not self.dry_run:
			os.makedirs(*args)

	def file_exists(self, file : str) -> bool:
		pass

