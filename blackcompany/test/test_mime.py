import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
from ..util._six import Path
import bottle
from . import utils
from .. import serve

serve.mime.Text.Markdown.serve('/index.md', '/webroot/index.md', template_file='/webroot/template.html')
serve.mime.Image.PNG.serve('/image', '/webroot/image.png')

@serve.mime.Text.Custom.custom()
def text_custom(route, filename):
	bottle.response.content_type = 'text/plain'
	return '[!CUSTOM: <<<{0}>>>]'.format(Path(filename).read_text())

serve.mime.Text.Custom.serve('/custom_text', '/webroot/custom.txt')

class TestMIMEEndpoints(utils.WebServerTestCase):
	def setUp(self):
		super(TestMIMEEndpoints, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[serve])
		self.fs.create_dir('/webroot')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')
		self.fs.create_file('/webroot/index.md', contents='# Index\n')
		self.fs.create_file('/webroot/image.png', contents='PNG...')
		self.fs.create_file('/webroot/custom.txt', contents='contents of the file')

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
