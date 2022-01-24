import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import os, subprocess
import tempfile, atexit
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
import bottle
from . import utils
from .. import serve

git_repo_root = tempfile.TemporaryDirectory(prefix='remote_')
atexit.register(git_repo_root.cleanup)
try:
	old_cwd = os.getcwd()
	os.chdir(str(git_repo_root.name))
	subprocess.check_call(['git', 'init', '--quiet', '.'])
	(Path(git_repo_root.name)/'test.txt').write_text('hello world')
	subprocess.check_call(['git', 'add', '.'])
	subprocess.check_call(['git', 'commit', '--quiet', '-m', 'Initial commit.'])
finally:
	os.chdir(old_cwd)

class TestGitBackend(utils.WebServerTestCase):
	def setUp(self):
		super(TestGitBackend, self).setUp()

		self.old_cwd = os.getcwd()
		os.chdir(str(git_repo_root.name))

		serve.vcs.git_repo('/gitrepo', git_repo_root.name)
	def tearDown(self):
		super(TestGitBackend, self).tearDown()
		os.chdir(self.old_cwd)

	def should_operate_on_remote_git_repo(self):
		with tempfile.TemporaryDirectory(prefix='local_') as local_copy:
			os.chdir(str(local_copy))
			subprocess.check_call(['git', 'clone', '--quiet', self._get_url('/gitrepo'), '.'])
			self.assertEqual((Path(local_copy)/'test.txt').read_text(), 'hello world')
			(Path(local_copy)/'test.txt').write_text('foo bar')
			subprocess.check_call(['git', 'add', '.'])
			subprocess.check_call(['git', 'commit', '--quiet', '-m', 'Test commit.'])
			# TODO: subprocess.check_call(['git', 'push', 'origin', 'master'])
