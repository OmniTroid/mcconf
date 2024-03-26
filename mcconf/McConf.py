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
        self.fileconf = self.complete_conf['conf']
        # Ask before applying each change
        self.prompt_changes = True
        self.rw_functions = {
            'properties': (McConf.read_properties_file, McConf.write_properties_file),
            'yml': (McConf.read_yml, McConf.write_yml)
        }

    # Invoked directly from terminal
    def init(self):
        if self.serverdir.exists():
            raise FileExistsError(self.serverdir)

        self.make_serverdir()
        self.write_eula()
        self.symlink_launcher()
        self.init_plugins()
        self.make_start_script()

        print('Done! Now run start.sh script to generate the initial state, then run init2')

    # HACK: Optimally, we want to generate the initial state in the init_server function
    # But as of today, we haven't succeeded into launching and stopping the server from python
    # So we have to do it manually for now. That is, run init, then run start.sh, then run init2
    def init2(self):
        print('Running step 2 of init')
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
                read_func, write_func = self.rw_functions[extension]
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

        McConf.replace_envs(delta_conf)

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

        original_path = Path(conf_path.parent, 'original_' + conf_path.name)

        if not original_path.exists():
            shutil.copy(conf_path, original_path)

        baseconf = read_func(conf_path)

        diff = McConf.dict_diff(baseconf, delta_conf)
        if diff == {}:
            print('No changes to apply')
            return

        result_conf = dc.merge_dicts([baseconf, diff])

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
        with open(path) as file:
            conf_str = file.read()

        # HACK: so Minecraft's server.properties actually lacks the section header.
        # configparse doesn't like this so we have to hack around that.
        if '[default]' not in conf_str:
            conf_str = '[default]\n' + conf_str

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

    # Replaces all envvars in the data dict with their corresponding values
    # In place, has no return value
    @staticmethod
    def replace_envs(data: dict):
        for key, value in data.items():
            if isinstance(value, str) and '{{' in value and '}}' in value:
                # Find value between {{ and }}
                envvar_key = value.split('{{')[1].split('}}')[0]
                envvar_value = os.getenv(envvar_key)
                if envvar_value is None or envvar_value == '':
                    logging.error(f'Environment variable {envvar_key} not found')
                    continue

                # Create variable new_value which replaces the envvar with the value
                new_value = value.replace('{{' + envvar_key + '}}', envvar_value)
                data[key] = new_value
            elif isinstance(value, dict):
                McConf.replace_envs(value)

    @staticmethod
    def dict_diff(whole_dict: {}, subset_dict: {}) -> {}:
        """
        Compares whole_dict and subset_dict. Returns the difference. Return a dict with a key and value for
        each value that is different. See the tests for a demonstration how this should work.
        Essentially, check if subset_dict is a strict subset of whole_dict, and return the difference
        Keys that aren't in both a and b are ignored
        :param subset_dict:
        :param whole_dict:
        :return: dict
        """
        diff = {}
        for key, value in subset_dict.items():
            if key in whole_dict:
                if isinstance(value, dict):
                    # Sanity check
                    if not isinstance(whole_dict[key], dict):
                        logging.error(f'Type mismatch between dicts with key {key}')
                        continue
                    subdiff = McConf.dict_diff(value, whole_dict[key])
                    if subdiff != {}:
                        diff[key] = subdiff
                elif value != whole_dict[key]:
                    diff[key] = value

        return diff
