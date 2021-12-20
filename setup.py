import setuptools
import re, subprocess
import sys

versions = sorted([
		m.group(1).split('.')
		for m in
		(re.match(r'^.*(\d+[.]\d+[.]\d+)$', line) for line in subprocess.check_output(['git', 'tag']).decode().splitlines())
		if m
		])
version = '.'.join(versions[-1]) if versions else '0.0.0'

py_version_requirements = []
if sys.version_info[0] == 2:
	py_version_requirements += [
			'pathlib2',
			]

setuptools.setup(
		name='blackcompany',
		version=version,
		packages=[
			'blackcompany',
			'blackcompany.util',
			],
		install_requires=[
			'six',
			'click',
			'bottle',
			'gevent',
			'markdown',
			'yaml',
			] + py_version_requirements,
		)
