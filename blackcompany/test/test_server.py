import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import sys
import socket
import functools
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
import bottle

from . import utils
from .. import _base
from .. import serve

@bottle.route('/test')
def test_page():
	return 'Hello, world!'

def track_user_agent(func):
	@functools.wraps(func)
	def _actual(*args, **kwargs):
		track_user_agent.history.append(bottle.request.get_header('User-Agent'))
		return func(*args, **kwargs)
	return _actual
track_user_agent.history = []
serve.mime.Text.Plain.serve('/tracker', '/webroot/trackme.txt', decorator=track_user_agent)

def track_remote_addr(remote_info):
	track_remote_addr.history.append(remote_info)
track_remote_addr.history = []
serve.mime.Text.Plain.serve('/track_ip', '/webroot/trackme.txt', on_remote_info=track_remote_addr)

class TestWebService(utils.WebServerTestCase):
	def setUp(self):
		super(TestWebService, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[_base, serve])
		self.fs.create_dir('/webroot')
		self.fs.create_file('/webroot/trackme.txt', contents='Hello, world!\n')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')

	def should_run_service(self):
		data = self._get('/test')
		self.assertEqual(data, b'Hello, world!')
	def should_call_custom_decorator(self):
		track_user_agent.history.clear()
		data = self._get('/tracker')
		self.assertEqual(data, b'Hello, world!\n')
		self.assertEqual(track_user_agent.history, ['Python-urllib/{0}.{1}'.format(*(sys.version_info[:2]))])
	def should_track_remote_info(self):
		track_remote_addr.history.clear()
		data = self._get('/track_ip')
		self.assertEqual(data, b'Hello, world!\n')
		current_ip = self.LOCALHOST
		current_name = socket.getnameinfo((current_ip, 0), 0)[0]
		self.assertEqual(track_remote_addr.history, [serve.RemoteInfo(current_ip, current_name)])
