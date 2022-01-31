import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import os, subprocess
import tempfile, atexit
from ..util import _six
from ..util._six import Path
import bottle
from . import utils
from .. import serve

git_repo_root = tempfile.TemporaryDirectory(prefix='remote_')
atexit.register(git_repo_root.cleanup)
try:
	old_cwd = os.getcwd()
	os.chdir(str(git_repo_root.name))
	subprocess.check_call(['git', 'init', '--quiet', '.'])
	subprocess.check_call(['git', 'config', '--local', '--add', 'receive.denyCurrentBranch', 'ignore']) # To allow pushing to this non-bare remote repo.
	(Path(git_repo_root.name)/'test.txt').write_text(u'hello world')
	subprocess.check_call(['git', 'add', '.'])
	subprocess.check_call(['git', 'commit', '--quiet', '-m', 'Initial commit.'])
	(Path(git_repo_root.name)/'.git'/'info'/'sparse-checkout').write_text(u'sparse-checkout')
finally:
	os.chdir(old_cwd)

git_bare_repo_root = tempfile.TemporaryDirectory(prefix='remote_bare_')
atexit.register(git_bare_repo_root.cleanup)
try:
	old_cwd = os.getcwd()
	os.chdir(str(git_bare_repo_root.name))
	subprocess.check_call(['git', 'init', '--quiet', '--bare', '.'])
finally:
	os.chdir(old_cwd)

class TestGitBackend(utils.WebServerTestCase):
	def setUp(self):
		super(TestGitBackend, self).setUp()

		self.old_cwd = os.getcwd()
		os.chdir(str(git_repo_root.name))

		serve.vcs.git_repo('/gitrepo', git_repo_root.name)
		serve.vcs.git_repo('/gitbarerepo', git_bare_repo_root.name)
	def tearDown(self):
		super(TestGitBackend, self).tearDown()
		os.chdir(self.old_cwd)

	def should_operate_on_remote_git_repo(self):
		with tempfile.TemporaryDirectory(prefix='local_') as local_copy:
			os.chdir(str(local_copy))
			subprocess.check_call(['git', 'clone', '--quiet', self._get_url('/gitrepo'), '.'])
			self.assertEqual((Path(local_copy)/'test.txt').read_text(), 'hello world')
			(Path(local_copy)/'test.txt').write_text(u'foo bar')
			subprocess.check_call(['git', 'add', '.'])
			subprocess.check_call(['git', 'commit', '--quiet', '-m', 'Test commit.'])
			subprocess.check_call(['git', 'push', '--quiet', 'origin', 'master'])
	def should_operate_on_remote_bare_git_repo(self):
		with tempfile.TemporaryDirectory(prefix='local_') as local_copy:
			os.chdir(str(local_copy))
			subprocess.check_output(['git', 'clone', '--quiet', self._get_url('/gitbarerepo'), '.'], stderr=subprocess.STDOUT) # To hide warning about "cloned an empty repository".
			(Path(local_copy)/'test.txt').write_text(u'foo bar')
			subprocess.check_call(['git', 'add', '.'])
			subprocess.check_call(['git', 'commit', '--quiet', '-m', 'Test commit.'])
			subprocess.check_call(['git', 'push', '--quiet', 'origin', 'master'])
	def should_fetch_git_info_files(self):
		data = self._get('/gitrepo/sparse-checkout')
		self.assertEqual(data, b'sparse-checkout')
