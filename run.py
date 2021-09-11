import argparse
import os
from pathlib import Path
import yaml
import pprint as pp

parser = argparse.ArgumentParser('Combine a set of yaml files into one')

parser.add_argument(
	'--serverdir',
	dest='serverdir',
	metavar='[serverdir]',
	help='Directory of the target server',
	required=True)
parser.add_argument(
	'--confdir',
	dest='confdir',
	metavar='[confdir]',
	help='Directory which contains config files to combine',
	required=True)

def main():
	args = parser.parse_args()

	yml_files = ['spigot.yml']
	serverdir = Path(args.serverdir).resolve()
	confdir = Path(args.confdir).resolve()

	if not serverdir.exists():
		raise FileNotFoundError(serverdir)

	if not serverdir.is_dir():
		raise NotADirectoryError(serverdir)

	if not confdir.exists():
		raise FileNotFoundError(confdir)

	if not confdir.is_dir():
		raise NotADirectoryError(confdir)

	for yml_file in yml_files:
		# The original yml
		base_yml = Path(serverdir, yml_file)

		with open(base_yml) as file:
			base_yml_data = yaml.safe_load(file)
			pp.PrettyPrinter(indent=4).pprint(base_yml_data)

		# List sub-yml files and sort alphabetically
		sub_yml_dir = Path(confdir, yml_file)
		sub_yml_files = sorted(
			[Path(filename) for filename in sub_yml_dir.iterdir()],
			key=lambda f: f.name)

		for sub_yml_file in sub_yml_files:
			with open(sub_yml_file) as file:
				sub_yml_data = yaml.safe_load(file)

			# Now we have base_yml_data (dict) and sub_yml_data. Wat nou?410

if __name__ == '__main__':
	main()