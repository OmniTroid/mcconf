from pathlib import Path

import pprint as pp

import fs2dict as f2d


def test_trivial():
    root_path = Path('')

    result = f2d.fs2dict(root_path)

    pp.pprint(result)

    assert True


def test_empty():
    empty_folder = Path('/tmp/fs2dict_empty')
    empty_folder.mkdir(exist_ok=True)

    result = f2d.fs2dict(empty_folder)

    assert result == {}
