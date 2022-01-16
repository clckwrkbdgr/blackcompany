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

serve.mime.Text.Markdown.serve('/index.md', '/webroot/index.md', template_file='/webroot/template.html')
serve.mime.Image.PNG.serve('/image', '/webroot/image.png')

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

@serve.mime.Text.Custom.custom()
def text_custom(route, filename):
	bottle.response.content_type = 'text/plain'
	return '[!CUSTOM: <<<{0}>>>]'.format(Path(filename).read_text())

serve.mime.Text.Custom.serve('/custom_text', '/webroot/custom.txt')

class TestWebService(utils.WebServerTestCase):
	def setUp(self):
		super(TestWebService, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[_base, serve])
		self.fs.create_dir('/webroot')
		self.fs.create_file('/webroot/trackme.txt', contents='Hello, world!\n')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')
		self.fs.create_file('/webroot/index.md', contents='# Index\n')
		self.fs.create_file('/webroot/image.png', contents='PNG...')
		self.fs.create_file('/webroot/custom.txt', contents='contents of the file')

	def should_run_service(self):
		data = self._get('/test')
		self.assertEqual(data, b'Hello, world!')
	def should_serve_arbitrary_mime_type(self):
		data, info = self._get('/image', with_info=True)
		self.assertEqual(info.get_content_type(), 'image/png')
		self.assertEqual(data, b'PNG...')
	def should_serve_mime_type_with_predefined_custom_handler(self):
		data, info = self._get('/index.md', with_info=True)
		self.assertEqual(info.get_content_type(), 'text/html')
		self.assertEqual(data, b'<html><head><title>Index</title></head><body><h1>Index</h1></body></html>\n')
	def should_serve_mime_type_with_custom_handler(self):
		data, info = self._get('/custom_text', with_info=True)
		self.assertEqual(info.get_content_type(), 'text/plain')
		self.assertEqual(data, b'[!CUSTOM: <<<contents of the file>>>]')
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
