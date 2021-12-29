import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import sys
import functools
import threading
import pyfakefs.fake_filesystem_unittest as fs_unittest
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
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
serve.markdown('/markdown', '/webroot/markdown/markdown.md', template_file='/webroot/template.html')
serve.mime.Text.Markdown.serve('/index.md', '/webroot/markdown/index.md', template_file='/webroot/template.html')
serve.plain_text('/raw_markdown', '/webroot/markdown/markdown.md')
serve.mime.Image.PNG.serve('/image', '/webroot/image.png')
serve.mime.Directory.List.serve('/dir', '/webroot/markdown', template_file='/webroot/template-index.html')
serve.mime.Directory.List.serve('/dir-external', '/webroot/markdown', template_file='/webroot/template.html', content_template_file='/webroot/template-index-content.html', title='Custom title')

def track_user_agent(func):
	@functools.wraps(func)
	def _actual(*args, **kwargs):
		track_user_agent.history.append(bottle.request.get_header('User-Agent'))
		return func(*args, **kwargs)
	return _actual
track_user_agent.history = []
serve.mime.Text.Plain.serve('/tracker', '/webroot/static/static.txt', decorator=track_user_agent)

@serve.mime.Text.Custom.custom()
def text_custom(route, filename):
	bottle.response.content_type = 'text/plain'
	return '[!CUSTOM: <<<{0}>>>]'.format(Path(filename).read_text())

serve.mime.Text.Custom.serve('/custom_text', '/webroot/custom.txt')

class TestWebService(fs_unittest.TestCase):
	LOCALHOST = '127.0.0.1'
	def setUp(self):
		self.setUpPyfakefs(modules_to_reload=[_base, serve])
		self.fs.create_dir('/webroot')
		self.fs.create_dir('/webroot/static')
		self.fs.create_file('/webroot/static/static.txt', contents='Hello, world!\n')
		self.fs.create_file('/webroot/as_is.html', contents='<html><body>Hello, world!</body></html>\n')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')
		index_content_template = '<ul>\n% for entry in entries:\n<li><a href="{{entry.path}}">{{entry.name}}</a></li>\n% end\n</ul>\n'
		self.fs.create_file('/webroot/template-index.html', contents='<html><head><title>{{title}}</title></head><body>'+index_content_template+'</body></html>\n')
		self.fs.create_file('/webroot/template-index-content.html', contents=index_content_template)
		self.fs.create_dir('/webroot/markdown')
		self.fs.create_file('/webroot/markdown/markdown.md', contents='**Hello, world!**\n')
		self.fs.create_file('/webroot/markdown/index.md', contents='# Index\n')
		self.fs.create_file('/webroot/image.png', contents='PNG...')
		self.fs.create_file('/webroot/custom.txt', contents='contents of the file')

		self._port = utils.get_free_tcp_port()
		self._service_thread = threading.Thread(target=_base.run, kwargs=dict(host=self.LOCALHOST, port=self._port, server_class=utils.StoppableServer))
		self._service_thread.daemon = True
		self._service_thread.start()
		utils.StoppableServer.instance().wait_for_start()
	def _get_url(self, path):
		return 'http://{0}:{1}/{2}'.format(self.LOCALHOST, self._port, path.lstrip('/'))
	def _get(self, path, with_info=False):
		response = urllib.request.urlopen(self._get_url(path))
		data = response.read()
		if with_info:
			data = data, response.info()
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
	def should_serve_plain_text(self):
		data = self._get('/raw_markdown')
		self.assertEqual(data, b'**Hello, world!**\n')
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
	def should_serve_directory_list_with_embedded_template(self):
		data = self._get('/dir')
		self.assertEqual(data, b'<html><head><title>Index of markdown</title></head><body><ul>\n<li><a href="/dir/index.md">index.md</a></li>\n<li><a href="/dir/markdown.md">markdown.md</a></li>\n</ul>\n</body></html>\n')
	def should_serve_directory_list_with_external_template(self):
		data = self._get('/dir-external')
		self.assertEqual(data, b'<html><head><title>Custom title</title></head><body><ul>\n<li><a href="/dir-external/index.md">index.md</a></li>\n<li><a href="/dir-external/markdown.md">markdown.md</a></li>\n</ul>\n</body></html>\n')
	def should_call_custom_decorator(self):
		track_user_agent.history.clear()
		data = self._get('/tracker')
		self.assertEqual(data, b'Hello, world!\n')
		self.assertEqual(track_user_agent.history, ['Python-urllib/{0}.{1}'.format(*(sys.version_info[:2]))])
