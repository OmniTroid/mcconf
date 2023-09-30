import os
import time
import subprocess
from pathlib import Path
from typing import Callable
import logging
import shutil

import yaml
import json
import configparser
import requests

import dictcombiner.dictcombiner as dc
import dir2dict as d2d


class UpdateConf:
    def __init__(self, args: {}):
        import coreconf
        self.coreconf = coreconf.coreconf
        self.java_dir = Path(self.coreconf['java_dir'])
        self.plugin_dir = Path(self.coreconf['plugin_dir'])
        self.launcher_dir = Path(self.coreconf['launcher_dir'])
        self.roles_dir = Path(self.coreconf['roles_dir'])

        self.args = args
        self.serverconf_path = Path(args['serverconf'])
        self.serverdir = Path(args['serverdir'])
        self.action = args['action']
        self.dry_run = args['dry_run']

        self.start_path = self.serverdir / 'start.sh'

        if not self.roles_dir.is_dir():
            logging.error(str(self.roles_dir) + ' is not a directory')
            raise NotADirectoryError

        if not self.serverdir.exists() and self.action != 'init':
            logging.error(str(self.serverdir) + ' is not a directory and action is not init')
            raise NotADirectoryError

        self.roles = json.loads(self.serverconf_path.read_text())['roles']
        self.role_dirs = []

        for role in self.roles:
            role_dir = self.roles_dir / role
            if not role_dir.is_dir():
                logging.error(str(role) + ' is not a directory')
                raise NotADirectoryError

            self.role_dirs.append(role_dir)

        roleconfs = self.get_roleconfs(self.roles)
        self.complete_conf = dc.merge_dicts(roleconfs)
        self.roleconf = self.complete_conf['roleconf.json']

    def init_server(self):
        if self.serverdir.exists():
            raise FileExistsError(self.serverdir)

        self.make_serverdir()
        self.write_eula()
        self.symlink_launcher()
        self.init_plugins()
        self.make_start_script()

        print('Done! Now run the start script to generate the initial state')

    # initserver functions #

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
            self.roleconf['launcher']
        )

        if 'launcher_version' in self.roleconf:
            launcher_file = self.roleconf['launcher_version'] + '.jar'
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

        plugins = self.roleconf['plugins'] if 'plugins' in self.roleconf else {}

        for plugin, plugin_conf in plugins.items():
            plugin_srcdir = Path(self.coreconf['plugin_dir'], plugin)

            if not plugin_srcdir.exists():
                print(f'WARNING: {plugin_srcdir} does not exist. Skipping plugin {plugin}')
                continue

            # Use the newest plugin in the plugin folder
            newest_plugin = sorted(
                (file for file in plugin_srcdir.iterdir()),
                key=lambda x: x.stat().st_mtime)[-1]

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

        if 'java_version' in self.roleconf:
            java_version = self.roleconf['java_version']
        else:
            java_version = 'latest'

        java_path = Path(self.coreconf['java_dir'], java_version)

        if not java_path.exists():
            print('WARNING: ' + str(java_path) + ' does not exist')

        memory = str(self.roleconf['memory'])
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

    # Update functions

    def update_all(self):
        self.update_server_properties()
        self.update_bukkit_yml()
        self.update_spigot_yml()
        self.update_paper_yml()

    # self.update_plugin_confs()

    def update_server_properties(self):
        baseconf_path = Path(self.serverdir, 'server.properties')
        if 'server.properties' not in self.conf:
            return
        delta_conf = self.conf['server.properties']
        self.update_conf(
            baseconf_path, delta_conf,
            self.read_properties_file, self.write_properties_file)

    def update_bukkit_yml(self):
        self.update_core_yml('bukkit')

    def update_spigot_yml(self):
        self.update_core_yml('spigot')

    def update_paper_yml(self):
        self.update_core_yml('paper')

    def update_plugin_confs(self):
        plugins_conf_dir = Path(self.confdir, 'plugins')

        if not plugins_conf_dir.exists():
            print('INFO: ' + str(plugins_conf_dir) + ' not found, skipping')
            return

        for dir_ in plugins_conf_dir.iterdir():
            pass
            # TODO: Add exceptions for plugins that dont have config.yml

            # conf_dir = Path(dir_)
            # conf_name = 'config.yml'
            # baseconf_path = Path(self.serverdir, 'plugins', conf_dir.name, 'config.yml')

    # Wrapper for updating core yml files (bukkit.yml, spigot.yml etc.)
    def update_core_yml(self, name: str):
        full_name = name + '.yml'
        core_yml_path = Path(self.serverdir, full_name)

        if full_name not in self.conf:
            return

        delta_conf = self.conf[full_name]

        self.update_conf(
            core_yml_path, delta_conf,
            self.read_yml, self.write_yml)

    # Updates the file given by conf_path based on the content of delta_conf
    # conf_path = the path to the config to update
    # delta_conf = the conf to "add" to the conf_path
    # read_func = a function that permits reading from the conf_path format
    # write_func = a function that permits writing to the conf_path format
    def update_conf(self, conf_path: Path, delta_conf: dict,
                    read_func: Callable, write_func: Callable):

        print('Applying conf to ' + str(conf_path))

        if self.dry_run:
            print(json.dumps(delta_conf, indent=4))
            return

        if not conf_path.exists():
            print('ERROR: ' + str(conf_path) + ' not found.')
            return

        original_path = Path(conf_path.parent, 'original_' + conf_path.name)

        # Use the original file if we have it
        # This means the script has been run before
        # This ensures idempotency
        if original_path.exists():
            baseconf = read_func(original_path)
        else:
            baseconf = read_func(conf_path)

        result_conf = dc.combine_dicts([baseconf, delta_conf])

        if not original_path.exists():
            conf_path.rename(original_path)

        write_func(conf_path, result_conf)

    # Takes a list of roles and returns a list of dicts containing the roleconf for each role
    def get_roleconfs(self, roles: list) -> [dict]:
        roleconfs = []

        for role in roles:
            confpath = Path(self.roles_dir, role)
            if not confpath.exists():
                raise FileNotFoundError(confpath)

            roleconfs.append(d2d.dir2dict(confpath))

        return roleconfs

    # Read and write helpers
    @staticmethod
    def read_properties_file(path: Path) -> dict:
        # HACK: so server.properties actually lacks the section header.
        # configparse doesn't like this so we have to hack around that.
        conf_str = '[default]\n'

        with open(path) as file:
            data = file.read()
            conf_str = conf_str + data

            tmp_conf = configparser.ConfigParser()
            tmp_conf.read_string(conf_str)

            conf = dict(tmp_conf.items('default'))

            return conf

    @staticmethod
    def write_properties_file(path: Path, data: dict):
        with open(path, 'w') as file:
            tmp_dict = {'default': data}
            tmp_conf = configparser.ConfigParser()
            tmp_conf.read_dict(tmp_dict)
            tmp_conf.write(file)

    @staticmethod
    def read_yml(path: Path) -> dict:
        with open(path) as file:
            data = yaml.safe_load(file)

        return data

    @staticmethod
    def write_yml(path: Path, data: dict):
        with open(path, 'w') as file:
            file.write(yaml.dump(data))
