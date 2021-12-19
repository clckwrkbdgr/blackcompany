import setuptools
import re, subprocess
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
		packages=['blackcompany'],
		install_requires=[
			'six',
			'click',
			'bottle',
			'gevent',
			],
		)
