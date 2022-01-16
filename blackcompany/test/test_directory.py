import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
from . import utils
from .. import _base
from .. import serve
from ..serve import directory, text

directory.static_content('/static', '/webroot/static/')
serve.mime.Directory.List.serve('/dir', '/webroot/markdown', template_file='/webroot/template-index.html')
serve.mime.Text.Markdown.serve('/dir', '/webroot/markdown', path_param='filename', template_file='/webroot/template.html', encoding='cp1251')
serve.mime.Directory.List.serve('/dir-external', '/webroot/markdown', template_file='/webroot/template.html', content_template_file='/webroot/template-index-content.html', title='Custom title')

class TestDirectoryHandlers(utils.WebServerTestCase):
	def setUp(self):
		super(TestDirectoryHandlers, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[_base, serve, directory, text])
		self.fs.create_dir('/webroot')
		self.fs.create_dir('/webroot/static')
		self.fs.create_file('/webroot/static/static.txt', contents='Hello, world!\n')
		self.fs.create_file('/webroot/template.html', contents='<html><head><title>{{title}}</title></head><body>{{!content}}</body></html>\n')
		index_content_template = '<ul>\n% for entry in entries:\n<li><a href="{{entry.path}}">{{entry.name}}</a></li>\n% end\n</ul>\n'
		self.fs.create_file('/webroot/template-index.html', contents='<html><head><title>{{title}}</title></head><body>'+index_content_template+'</body></html>\n')
		self.fs.create_file('/webroot/template-index-content.html', contents=index_content_template)
		self.fs.create_dir('/webroot/markdown')
		self.fs.create_file('/webroot/markdown/markdown.md', contents='**Hello, world!**\n')
		self.fs.create_file('/webroot/markdown/index.md', contents='# Index\n')
		self.fs.create_file('/webroot/markdown/cp1251.md', contents='Привет, мир\n'.encode('cp1251'))
	def should_serve_static_content(self):
		data = self._get('/static/static.txt')
		self.assertEqual(data, b'Hello, world!\n')
	def should_serve_directory_list_with_embedded_template(self):
		data = self._get('/dir')
		self.assertEqual(data, b'<html><head><title>Index of markdown</title></head><body><ul>\n<li><a href="/dir/cp1251.md">cp1251.md</a></li>\n<li><a href="/dir/index.md">index.md</a></li>\n<li><a href="/dir/markdown.md">markdown.md</a></li>\n</ul>\n</body></html>\n')
	def should_serve_directory_content_with_specific_mime_type(self):
		data = self._get('/dir/index.md')
		self.assertEqual(data, b'<html><head><title>Index</title></head><body><h1>Index</h1></body></html>\n')
		data = self._get('/dir/markdown.md')
		self.assertEqual(data, b'<html><head><title>markdown</title></head><body><p><strong>Hello, world!</strong></p></body></html>\n')
		data = self._get('/dir/cp1251.md')
		self.assertEqual(data, '<html><head><title>cp1251</title></head><body><p>Привет, мир</p></body></html>\n'.encode('utf-8'))
	def should_serve_directory_list_with_external_template(self):
		data = self._get('/dir-external')
		self.assertEqual(data, b'<html><head><title>Custom title</title></head><body><ul>\n<li><a href="/dir-external/cp1251.md">cp1251.md</a></li>\n<li><a href="/dir-external/index.md">index.md</a></li>\n<li><a href="/dir-external/markdown.md">markdown.md</a></li>\n</ul>\n</body></html>\n')
