import json
import yaml
import configparser
from pathlib import Path


def parse_json(path: Path) -> dict:
    with open(path) as file:
        data = file.read()

    return json.loads(data)


def parse_yml(path: Path) -> dict:
    with open(path) as file:
        data = yaml.safe_load(file)

    return data


def parse_properties(path: Path) -> dict:
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


formatparsers = {
	"json": parse_json,
	"yml": parse_yml,
	"properties": parse_properties
}
