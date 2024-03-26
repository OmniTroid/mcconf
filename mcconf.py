#!/usr/bin/env python3

# This script takes an existing Minecraft server and
# updates the config based on the

import os
import argparse

import dotenv

import mcconf


def main():
	parser = argparse.ArgumentParser('Minecraft server config tool')

	parser.add_argument(
		'--confdir',
		dest='confdir',
		metavar='[confdir]',
		help='Path to the confdir of the server to create. \
Should contain at least a baseconf.json. Can contain a conf directory.',
		required=True)
	parser.add_argument(
		'--serverdir',
		dest='serverdir',
		metavar='[serverdir]',
		help='Path of the server directory. In case of init, it should not already exist.',
		default='.')
	parser.add_argument(
		'--dry-run',
		dest='dry_run',
		help='Just print commands, do not actually run anything',
		action='store_true')
	parser.add_argument(
		'--envfile',
		dest='envfile',
		metavar='[envfile]',
		help='Path to an envfile to load')
	parser.add_argument(
		dest='action',
		metavar='[action]',
		help='Action to take. Valid actions: init, init2, update')

	args = vars(parser.parse_args())

	if 'envfile' in args:
		dotenv.load_dotenv(args['envfile'])

	mco = mcconf.McConf(args)

	if args['action'] == 'init':
		mco.init()
	elif args['action'] == 'update':
		mco.update()
	else:
		print('Unknown action: ' + args['action'])


if __name__ == '__main__':
	main()
