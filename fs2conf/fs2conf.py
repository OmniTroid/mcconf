from pathlib import Path

from . import formatparsers as fp
from .dictcombiner import utils as dc


# Combine all files in the given directory
def combine_confs(conf_dir: Path) -> dict:
    # This means the file has no config, which is perfectly valid
    if not conf_dir.exists():
        print('INFO: ' + str(conf_dir) + ' not found.')
        return {}

    extension = conf_dir.name.split('.')[-1]

    if extension not in fp.formatparsers:
        print('Error: unknown format for file: ' + conf_dir.name)
        raise Exception

    read_func = fp.formatparsers[extension]

    subconf_files = sorted(
        [Path(filename) for filename in conf_dir.iterdir()],
        key=lambda f: f.name)

    subconfs = []

    for subconf_file in subconf_files:
        subconfs.append(read_func(subconf_file))

    result_conf = dc.combine_dicts(subconfs)

    return result_conf


# Traverses the given dir and build a fully combined conf tree
def fs2conf(dir_: Path) -> dict:
    if not dir_.is_dir():
        raise NotADirectoryError(dir_)

    conf = {}

    for child in dir_.iterdir():
        subconf = {}

        if child.is_file():
            if child.name.endswith('.json'):
                subconf = fh.parse_json(child)

        elif child.is_dir():
            # This means the dir contains a set of files to be combined to one
            if '.' in child.name:
                subconf = combine_confs(child)
            else:
                subconf = fs2conf(child)
        else:
            print('Error: not a file or directory! ' + child.name)

        conf[child.name] = subconf

    return conf


# Combine the given list of paths to a dict
def combine_dirs(dirs: [Path]) -> dict:
    confs = []

    for dir_ in dirs:
        if not dir_.is_dir():
            print('Warning: ' + str(dir_) + ' is not a directory.')
            continue

        confs.append(fs2conf(dir_))

    result_conf = dc.combine_dicts(confs)

    return result_conf
