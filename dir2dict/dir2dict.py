from pathlib import Path
import logging

from . import formatparsers as fp


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
        if extension in fp.formatparsers:
            conf[child.name] = fp.formatparsers[extension](child)
            continue
        else:
            logging.warning(f"Unknown file extension: {extension}")

    return conf
