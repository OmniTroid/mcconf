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


def test_merge_lists():
    list_a = [1, 1, 2, 3]
    list_b = [4, 5, 6]
    result = f2c.dc.merge_lists(list_a, list_b)
    expected = [1, 2, 3, 4, 5, 6]

    assert result == expected


def test_merge_lists_in_dict():
    dict_a = {
        "a": [1, 1, 2, 3],
        "b": [4, 5, 6]
    }

    dict_b = {
        "a": [7, 8, 9],
        "b": [10, 11, 12]
    }

    expected = {
        "a": [1, 2, 3, 7, 8, 9],
        "b": [4, 5, 6, 10, 11, 12]
    }

    result = f2c.dc.merge_dicts(dict_a, dict_b)
    assert result == expected


def test_merge_dicts():
    dict_a = {
        "a": 1,
        "b": 2
    }

    dict_b = {
        "c": 3,
        "d": 4
    }

    expected = {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4
    }

    result = f2c.dc.merge_dicts(dict_a, dict_b)
    assert result == expected
