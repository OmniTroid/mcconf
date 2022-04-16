from pathlib import Path

from . import formatparsers as fp
from .dictcombiner import utils as dc


def get_extension(path: Path):
    return path.name.split('.')[-1]


# Take a file or directory of a known format and creates a combined dict
def format_to_dict(path: Path) -> dict:
    extension = get_extension(path)
    read_func = fp.formatparsers[extension]

    if path.is_file():
        return read_func(path)

    files = sorted(
        [Path(filename) for filename in path.iterdir()],
        key=lambda f: f.name)

    return dc.combine_dicts(read_func(file) for file in files)


# Traverse the given dir and build a fully combined dict
def fs2dict(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError
    if not path.is_dir():
        raise NotADirectoryError

    conf = {}

    for child in path.iterdir():
        extension = get_extension(child)
        if extension in fp.formatparsers:
            conf[child.name] = format_to_dict(child)
            continue

        if child.is_dir():
            conf[child.name] = fs2dict(child)
            continue

    return conf
