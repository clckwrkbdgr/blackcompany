import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import threading
import pyfakefs.fake_filesystem_unittest as fs_unittest
from six.moves import urllib
import bottle

from . import utils
from .. import _base
from .. import serve

@bottle.route('/test')
def test_page():
	return 'Hello, world!'

serve.static_content('/static', '/webroot/static/')
serve.html('/as_is', '/webroot/as_is.html')
serve.markdown('/markdown', '/webroot/markdown.md', template_file='/webroot/template.html')
serve.plain_text('/raw_markdown', '/webroot/markdown.md')

class TestWebService(fs_unittest.TestCase):
	LOCALHOST = '127.0.0.1'
	def setUp(self):
		self.setUpPyfakefs(modules_to_reload=[_base, serve])
		self.fs.create_dir('/webroot')
		self.fs.create_dir('/webroot/static')
		self.fs.create_file('/webroot/static/static.txt', contents='Hello, world!\n')
		self.fs.create_file('/webroot/as_is.html', contents='<html><body>Hello, world!</body></html>\n')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')
		self.fs.create_file('/webroot/markdown.md', contents='**Hello, world!**\n')

		self._port = utils.get_free_tcp_port()
		self._service_thread = threading.Thread(target=_base.run, kwargs=dict(host=self.LOCALHOST, port=self._port, server_class=utils.StoppableServer))
		self._service_thread.daemon = True
		self._service_thread.start()
		utils.StoppableServer.instance().wait_for_start()
	def _get_url(self, path):
		return 'http://{0}:{1}/{2}'.format(self.LOCALHOST, self._port, path.lstrip('/'))
	def _get(self, path):
		req = urllib.request.urlopen(self._get_url(path))
		data = req.read()
		return data
	def tearDown(self):
		utils.StoppableServer.instance().shutdown()
		self._service_thread.join()

	def should_run_service(self):
		data = self._get('/test')
		self.assertEqual(data, b'Hello, world!')
	def should_serve_static_content(self):
		data = self._get('/static/static.txt')
		self.assertEqual(data, b'Hello, world!\n')
	def should_serve_html_as_is(self):
		data = self._get('/as_is')
		self.assertEqual(data, b'<html><body>Hello, world!</body></html>\n')
	def should_serve_markdown_in_template(self):
		data = self._get('/markdown')
		self.assertEqual(data, b'<html><head><title>markdown</title></head><body><p><strong>Hello, world!</strong></p></body></html>\n')
	def should_plain_text(self):
		data = self._get('/raw_markdown')
		self.assertEqual(data, b'**Hello, world!**\n')
