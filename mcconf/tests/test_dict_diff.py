import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
script_dir = os.path.dirname(os.path.realpath(__file__))

from McConf import McConf


def test_single_diff():
    full_conf = {
        'server': {
            'properties': {
                'level-name': 'world',
                'server-port': '25565'
            }
        }
    }

    delta_conf = {
        'server': {
            'properties': {
                'server-port': '25566'
            }
        }
    }

    diff = McConf.dict_diff(full_conf, delta_conf)
    assert diff == {
        'server': {
            'properties': {
                'server-port': '25566'
            }
        }
    }


def test_identical():
    full_conf = {
        'server': {
            'properties': {
                'level-name': 'world',
                'server-port': '25565'
            }
        }
    }

    delta_conf = {
        'server': {
            'properties': {
                'level-name': 'world',
                'server-port': '25565'
            }
        }
    }

    diff = McConf.dict_diff(full_conf, delta_conf)
    assert diff == {}
