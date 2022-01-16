import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
from . import utils
from .. import _base
from ..serve import text

text.html('/as_is', '/webroot/as_is.html')
text.markdown('/markdown', '/webroot/markdown/markdown.md', template_file='/webroot/template.html')
text.plain_text('/raw_markdown', '/webroot/markdown/markdown.md')

class TestTextCustomizations(utils.WebServerTestCase):
	def setUp(self):
		super(TestTextCustomizations, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[_base, text])
		self.fs.create_file('/webroot/as_is.html', contents='<html><body>Hello, world!</body></html>\n')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')
		self.fs.create_dir('/webroot/markdown')
		self.fs.create_file('/webroot/markdown/markdown.md', contents='**Hello, world!**\n')
	def should_serve_html_as_is(self):
		data = self._get('/as_is')
		self.assertEqual(data, b'<html><body>Hello, world!</body></html>\n')
	def should_serve_plain_text(self):
		data = self._get('/raw_markdown')
		self.assertEqual(data, b'**Hello, world!**\n')
	def should_serve_markdown_in_template(self):
		data = self._get('/markdown')
		self.assertEqual(data, b'<html><head><title>markdown</title></head><body><p><strong>Hello, world!</strong></p></body></html>\n')
