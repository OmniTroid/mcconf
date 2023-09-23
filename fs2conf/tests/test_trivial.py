import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from fs2conf import fs2conf as f2c


def test_trivial():
    root_path = Path('')
    result = f2c.fs2conf(root_path)
    assert True


def test_empty():
    empty_folder = Path('/tmp/fs2dict_empty')
    empty_folder.mkdir(exist_ok=True)

    result = f2c.fs2conf(empty_folder)

    assert result == {}

