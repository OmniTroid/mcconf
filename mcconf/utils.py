from pathlib import Path
import logging
import os

from .rw_functions import rw_functions as rf


# Traverse the given directory and construct a dictionary that represents the file structure
def dir2dict(path: Path) -> dict:
    if not path.is_dir():
        raise NotADirectoryError

    conf = {}

    for child in path.iterdir():
        if child.is_dir():
            conf[child.name] = dir2dict(child)
            continue

        extension = child.name.split('.')[-1]
        if extension in rf:
            # Call the read function for the extension
            conf[child.name] = rf[extension][0](child)
            continue
        else:
            logging.warning(f"Unknown file extension: {extension}")

    return conf


# Loads a complete config from a path
def load_conf(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)

    conf = dir2dict(path)
    return conf


# Replaces all envvars in the data dict with their corresponding values
# In place, has no return value
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
            replace_envs(value)


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
                subdiff = dict_diff(whole_dict[key], value)
                if subdiff != {}:
                    diff[key] = subdiff
            elif value != whole_dict[key]:
                diff[key] = value

    return diff
