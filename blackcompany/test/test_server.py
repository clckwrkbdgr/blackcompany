import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import sys
import socket
import functools
from ..util._six import Path
import six
from ..util import _six
import bottle
import pyfakefs.fake_filesystem_unittest as fs_unittest

from . import utils
from .. import _base
from .. import serve
from ..util import adhocserver

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
		del track_user_agent.history[:] # Py2 has no .clear()
		data = self._get('/tracker')
		self.assertEqual(data, b'Hello, world!\n')
		self.assertEqual(track_user_agent.history, ['Python-urllib/{0}.{1}'.format(*(sys.version_info[:2]))])
	def should_track_remote_info(self):
		del track_remote_addr.history[:] # Py2 has no .clear()
		data = self._get('/track_ip')
		self.assertEqual(data, b'Hello, world!\n')
		current_ip = self.LOCALHOST
		current_name = socket.getnameinfo((current_ip, 0), 0)[0]
		self.assertEqual(track_remote_addr.history, [serve.RemoteInfo(current_ip, current_name)])

class TestAdhocBackgroundService(fs_unittest.TestCase):
	def should_run_adhoc_background_service_as_context_manager(self):
		with adhocserver.AdhocBackgroundServer() as server:
			url = 'http://{0}:{1}/test'.format(server.hostname, server.port)
			request = _six.Request(url)
			response = _six.urlopen(request)
			data = response.read()
			self.assertEqual(data, b'Hello, world!')
