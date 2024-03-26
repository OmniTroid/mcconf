from pathlib import Path
import json
import io

import configparser
import yaml


# Read and write helpers
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


def write_properties_file(path: Path, data: dict):
    with open(path, 'w') as file:
        tmp_dict = {'default': data}
        tmp_conf = configparser.ConfigParser()
        tmp_conf.read_dict(tmp_dict)
        buffer = io.StringIO()
        tmp_conf.write(buffer)

        # HACK: So it turns out that minecraft mangles valid .properties files by treating [default] as a key...
        # need to do this terribleness to write a "minecraft-friendly" properties file.
        file.write(buffer.getvalue().replace('[default]\n', ''))


def read_yml(path: Path) -> dict:
    with open(path) as file:
        data = yaml.safe_load(file)

    return data


def write_yml(path: Path, data: dict):
    with open(path, 'w') as file:
        file.write(yaml.dump(data))


def read_json(path: Path) -> dict:
    with open(path) as file:
        data = file.read()

    return json.loads(data)


def write_json(path: Path, data: dict):
    with open(path, 'w') as file:
        file.write(json.dumps(data, indent=4))


rw_functions = {
    'properties': (read_properties_file, write_properties_file),
    'yml': (read_yml, write_yml),
    'json': (read_json, write_json)
}
