import os

from .. import utils

script_dir = os.path.dirname(os.path.realpath(__file__))


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

    diff = utils.dict_diff(full_conf, delta_conf)
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

    diff = utils.dict_diff(full_conf, delta_conf)
    assert diff == {}
