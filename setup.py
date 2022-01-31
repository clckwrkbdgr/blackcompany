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

setuptools.setup(
		name='blackcompany',
		version=version,
		packages=[
			'blackcompany',
			'blackcompany.serve',
			'blackcompany.util',
			],
		install_requires=[
			'six',
			'click',
			'bottle',
			'gevent',
			'markdown',
			'jinja2',
			'pyyaml',

			'pathlib2;python_version<="2.7"',
			'backports.functools-lru-cache;python_version<="2.7"',
			'backports.tempfile;python_version<="2.7"',
			]
		)
