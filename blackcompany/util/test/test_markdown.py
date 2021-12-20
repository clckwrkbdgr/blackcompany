import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import pyfakefs.fake_filesystem_unittest as fs_unittest
try:
	from pathlib2 import Path
except ImportError: # pragma: no cover
	from pathlib import Path
from .. import markdown

WITHOUT_YAML = """# heading

**List**:

- foo
- bar
"""

WITH_YAML = """---
key: value
names: [foo, bar, baz]
---
""" + WITHOUT_YAML

class TestMarkdownFile(fs_unittest.TestCase):
	def setUp(self):
		self.setUpPyfakefs(modules_to_reload=[markdown])
		self.fs.create_dir('/data')
	def should_init_empty_file(self):
		md = markdown.MarkdownFile()
		self.assertIsNone(md.filename)
		self.assertEqual(md.header, {})
		self.assertEqual(md.text, '')
	def should_load_from_content(self):
		md = markdown.MarkdownFile(content=WITHOUT_YAML)
		self.assertIsNone(md.filename)
		self.assertEqual(md.header, {})
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_load_from_content_with_header(self):
		md = markdown.MarkdownFile(content=WITH_YAML)
		self.assertIsNone(md.filename)
		self.assertEqual(md.header, {
			'key' : 'value',
			'names' : ['foo', 'bar', 'baz'],
			})
		self.assertEqual(md.header.key, 'value')
		self.assertEqual(md.header.names, ['foo', 'bar', 'baz'])
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_skip_incomplete_header(self):
		md = markdown.MarkdownFile(content='---\nkey: value\n' + WITHOUT_YAML)
		self.assertIsNone(md.filename)
		self.assertEqual(md.header, {})
		self.assertEqual(md.text, '---\nkey: value\n' + WITHOUT_YAML)
	def should_load_from_file(self):
		self.fs.create_file('/data/filename.md', contents=WITH_YAML)
		md = markdown.MarkdownFile(filename='/data/filename.md')
		self.assertEqual(md.filename, Path('/data/filename.md'))
		self.assertEqual(md.header, {
			'key' : 'value',
			'names' : ['foo', 'bar', 'baz'],
			})
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_not_load_from_file_when_content_is_given(self):
		self.fs.create_file('/data/filename.md', contents=WITH_YAML)
		md = markdown.MarkdownFile(filename='/data/filename.md', content=WITHOUT_YAML)
		self.assertEqual(md.filename, Path('/data/filename.md'))
		self.assertEqual(md.header, {})
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_convert_parsed_file_back_to_string(self):
		md = markdown.MarkdownFile(content=WITHOUT_YAML)
		self.assertEqual(str(md), WITHOUT_YAML)

		md = markdown.MarkdownFile(content=WITH_YAML)
		self.assertEqual(str(md), WITH_YAML)
