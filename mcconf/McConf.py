import os
import time
import subprocess
from pathlib import Path
from typing import Callable
import logging
import shutil
import copy

import json
import requests

import dictcombiner.dictcombiner as dc
import utils
from rw_functions import rw_functions


class McConf:
    def __init__(self, args: {}):
        import coreconf
        self.coreconf = coreconf.coreconf
        self.java_dir = Path(self.coreconf['java_dir'])
        self.bukkit_plugin_dir = Path(self.coreconf['bukkit_plugin_dir'])
        self.launcher_dir = Path(self.coreconf['launcher_dir'])
        self.roles_dir = Path(self.coreconf['roles_dir'])

        self.args = args
        self.serverconf_path = Path(args['serverconf'])
        self.serverdir = Path(args['serverdir'])
        self.action = args['action']
        self.dry_run = args['dry_run']

        self.start_path = self.serverdir / 'start.sh'

        if not self.serverdir.exists() and self.action != 'init':
            logging.error(str(self.serverdir) + ' is not a directory and action is not init')
            raise NotADirectoryError

        self.baseconf = utils.load_conf(self.serverconf_path / 'baseconf.json')
        self.fileconf = utils.load_conf(self.serverconf_path / 'conf')
        # Ask before applying each change
        self.prompt_changes = True

    # Invoked directly from terminal
    def init(self):
        if self.serverdir.exists():
            raise FileExistsError(self.serverdir)

        self.make_serverdir()
        self.write_eula()
        self.symlink_launcher()
        self.init_plugins()
        self.make_start_script()

        print('Done! Now run start.sh script to generate the initial state, then run update')

    # HACK: Optimally, we want to generate the initial state in the init_server function
    # But as of today, we haven't succeeded into launching and stopping the server from python
    # So we have to do it manually for now. That is, run init, then run start.sh, then run update
    def update(self):
        print('Running update')
        self.update_recursively(self.fileconf, self.serverdir)

    # Update the server based on the serverconf
    # Run recursively. Take conf as argument, which is a dict consisting of
    # Filenames as keys and the conf to apply as values
    def update_recursively(self, fileconf: dict, path: Path):
        for filename, conf in fileconf.items():
            existing_conf_path = Path(path, filename)

            # Here we make the assumption that all generated config modifies existing config
            # This assumption may not hold in the future
            if not existing_conf_path.exists():
                logging.warning(f'{filename} exists in config, but not in server. Skipping.')
                continue

            if existing_conf_path.is_file():
                extension = existing_conf_path.suffix[1:]
                read_func, write_func = rw_functions[extension]
                self.update_conf(existing_conf_path, conf, read_func, write_func)
            elif existing_conf_path.is_dir():
                self.update_recursively(conf, existing_conf_path)

# Init functions

    def make_serverdir(self):
        print('### Make server directory')
        if self.serverdir.exists():
            print('INFO: ' + str(self.serverdir) + ' already exists, skipping mkdir step.')
        else:
            self.serverdir.mkdir()

    def write_eula(self):
        print('### Write eula file')

        eula_path = Path(self.serverdir, 'eula.txt')

        with open(eula_path, 'w') as file:
            file.write('eula=true\n')

    def symlink_launcher(self):
        print('### Symlink launcher')

        launcher_dir = Path(
            self.coreconf['launcher_dir'],
            self.baseconf['launcher']
        )

        if 'launcher_version' in self.baseconf:
            launcher_file = self.baseconf['launcher_version'] + '.jar'
        # If there is no specific version, use the newest(latest) launcher
        else:
            launcher_file = sorted(
                (file for file in launcher_dir.iterdir()),
                key=lambda x: x.stat().st_mtime)[-1]

        launcher_src = Path(
            launcher_dir,
            launcher_file
        )

        if not launcher_src.exists():
            print('ERROR: ' + str(launcher_src) + ' does not exist')
            raise FileNotFoundError

        launcher_dst = Path(self.serverdir, 'server.jar')

        if launcher_dst.exists():
            print('INFO: ' + str(launcher_dst) + ' exists, skipping symlink step.')
        else:
            os.symlink(launcher_src, launcher_dst)

    def init_plugins(self):
        print('### Init plugins')
        server_plugin_dir = Path(self.serverdir, 'plugins')

        if not server_plugin_dir.exists():
            server_plugin_dir.mkdir()

        plugins = self.baseconf['plugins'] if 'plugins' in self.baseconf else {}

        for plugin, plugin_conf in plugins.items():
            plugin_srcdir = Path(self.coreconf['bukkit_plugin_dir'], plugin)

            if not plugin_srcdir.exists():
                print(f'WARNING: {plugin_srcdir} does not exist. Skipping plugin {plugin}')
                continue

            # Use the newest plugin in the plugin folder
            newest_plugin = sorted(
                (file for file in plugin_srcdir.iterdir()),
                key=lambda x: x.stat().st_mtime)[-1].name

            plugin_src = Path(plugin_srcdir, newest_plugin)
            plugin_dst = Path(server_plugin_dir, newest_plugin)

            if plugin_dst.exists():
                logging.info(f'WARNING: plugin symlink {plugin_dst} exists, skipping.')
                continue

            # TODO: We should write the filename to a lockfile so we can check and update it later
            shutil.copy(plugin_src, plugin_dst)

    # Download and modify start script
    def make_start_script(self):
        print('### Make start script')

        if self.start_path.exists():
            print('# INFO: ' + str(self.start_path) + ' already exists. Skipping step.')

        response = requests.get(
            # 'http://tiny.cc/mcstart',
            """https://gist.githubusercontent.com/OmniTroid/267730675631383ce3651155405b3474\
            /raw/95bc84a677df065ebe032eeda5db5c2b72438d59/start.sh""",
            headers={'User-Agent': 'mcconf'})

        if response.status_code != 200:
            raise ConnectionError

        start_script = response.text

        if 'java_version' in self.baseconf:
            java_version = self.baseconf['java_version']
        else:
            java_version = 'latest'

        java_path = Path(self.coreconf['java_dir'], java_version)

        if not java_path.exists():
            print('WARNING: ' + str(java_path) + ' does not exist')

        memory = str(self.baseconf['memory'])
        start_script = start_script.replace(
            'java', str(java_path)
        ).replace(
            'paperclip.jar',
            'server.jar'
        ).replace(
            'Xms10G',
            f'Xms{memory}G'
        ).replace(
            'Xmx10G',
            f'Xmx{memory}G')

        self.start_path.write_text(start_script)

        # Make executable
        st = self.start_path.stat()
        self.start_path.chmod(st.st_mode | 0o111)

    # Start server and generate initial state
    def generate_initial_state(self):
        print('### Generate initial state')
        print(self.start_path)
        print('Starting server process')
        child_process = subprocess.Popen(
            self.start_path,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        # Give it some time to set up
        print('Waiting 20 seconds...')
        time.sleep(20)

        # FIXME: child never responds to kill signal for some reason

        print('Killing server process')
        child_process.kill()

        print('Initial generation complete.')

    # Updates the file given by conf_path based on the content of delta_conf
    # conf_path = the path to the config to update
    # delta_conf = the conf to "add" to the conf_path
    # read_func = a function that permits reading from the conf_path format
    # write_func = a function that permits writing to the conf_path format
    def update_conf(self, conf_path: Path, delta_conf: dict,
                    read_func: Callable, write_func: Callable):

        if not conf_path.exists():
            logging.error(str(conf_path) + ' not found.')
            return

        baseconf = read_func(conf_path)

        # replace_envs replaces in-place so make a copy so we don't change the incoming args
        delta_conf = copy.deepcopy(delta_conf)
        utils.replace_envs(delta_conf)

        diff = utils.dict_diff(baseconf, delta_conf)
        if diff == {}:
            print(f'Config is up-to-date: {conf_path}')
            return

        print('Applying following conf to ' + str(conf_path))
        print(json.dumps(delta_conf, indent=4))

        if self.dry_run:
            print('Dry run. Skipping...')
            return

        if self.prompt_changes:
            response = input('Apply changes? [y/n] ')
            if response != 'y':
                print('Skipping...')
                return

        result_conf = dc.merge_dicts([baseconf, diff])

        original_path = Path(conf_path.parent, 'original_' + conf_path.name)

        # If there is no original file, this is the first time mcconf has been run on this config file
        # So make a backup of the original file
        if not original_path.exists():
            shutil.copy(conf_path, original_path)

        write_func(conf_path, result_conf)
