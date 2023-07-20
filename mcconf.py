#!/usr/bin/env python3

# This script takes an existing Minecraft server and
# updates the config based on the

import argparse

import mcconf


def main():
	parser = argparse.ArgumentParser('Minecraft server config tool')

	parser.add_argument(
		'--role',
		dest='role',
		metavar='[role]',
		help='Name of the role to use. Based on this and roles_dir in coreconf.py, the appropriate\
roleconf.json will be loaded',
		required=True)
	parser.add_argument(
		'--name',
		dest='name',
		metavar='[name]',
		help='Name of the server to create',
		required=True)
	parser.add_argument(
		'--serversdir',
		dest='serversdir',
		metavar='[serversdir]',
		help='Directory to create the server in. Defaults to current working directory.',
		default='.')
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
