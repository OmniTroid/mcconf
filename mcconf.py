#!/usr/bin/env python3

# This script takes an existing Minecraft server and
# updates the config based on the

import argparse

import mcconf


def main():
	parser = argparse.ArgumentParser('Minecraft server config tool')

	parser.add_argument(
		'--serverconf',
		dest='serverconf',
		metavar='[serverconf]',
		help='Path to serverconf.json',
		required=True)
	parser.add_argument(
		'--serverdir',
		dest='serverdir',
		metavar='[serverdir]',
		help='Directory of the target server',
		required=True)
	parser.add_argument(
		'--dry-run',
		dest='dry_run',
		help='Just print commands, do not actually run anything',
		action='store_true')
	parser.add_argument(
		dest='action',
		metavar='[action]',
		help='Action to take. Valid actions: init, update')

	args = vars(parser.parse_args())

	uc = mcconf.UpdateConf(args)

	if args['action'] == 'init':
		uc.init_server()
	elif args['action'] == 'update':
		uc.update_all()
	else:
		print('Unknown action: ' + args['action'])


if __name__ == '__main__':
	main()
