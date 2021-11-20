from pathlib import Path
import os
import pprint as pp

import fs2conf as f2c

def test_trivial():

	root_path = Path('/Users/dskoland/projects/mc/mc.buk.gg-conf/base')

	result = f2c.fs2conf(dir_=root_path)

	pp.pprint(result)

	assert True

def test_empty():
	empty_folder = Path('/tmp/fs2conf_empty')
	empty_folder.mkdir(exist_ok=True)

	result = f2c.fs2conf(dir_=empty_folder)

	assert result == {}
