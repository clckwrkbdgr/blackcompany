import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import pyfakefs.fake_filesystem_unittest as fs_unittest
try:
	from pathlib2 import Path
except ImportError: # pragma: no cover
	from pathlib import Path
import json
from .. import markdown

WITHOUT_YAML = """# heading

**List**:

- foo
- bar
"""

WITH_YAML = """---
names:
- foo
- bar
- baz
title: Note
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
			'title' : 'Note',
			'names' : ['foo', 'bar', 'baz'],
			})
		self.assertEqual(md.header.title, 'Note')
		self.assertEqual(md.header.names, ['foo', 'bar', 'baz'])
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_skip_incomplete_header(self):
		md = markdown.MarkdownFile(content='---\ntitle: Note\n' + WITHOUT_YAML)
		self.assertIsNone(md.filename)
		self.assertEqual(md.header, {})
		self.assertEqual(md.text, '---\ntitle: Note\n' + WITHOUT_YAML)
	def should_load_from_file(self):
		self.fs.create_file('/data/filename.md', contents=WITH_YAML)
		md = markdown.MarkdownFile(filename='/data/filename.md')
		self.assertEqual(md.filename, Path('/data/filename.md'))
		self.assertEqual(md.header, {
			'title' : 'Note',
			'names' : ['foo', 'bar', 'baz'],
			})
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_not_load_from_file_when_content_is_given(self):
		self.fs.create_file('/data/filename.md', contents=WITH_YAML)
		md = markdown.MarkdownFile(filename='/data/filename.md', content=WITHOUT_YAML)
		self.assertEqual(md.filename, Path('/data/filename.md'))
		self.assertEqual(md.header, {})
		self.assertEqual(md.text, WITHOUT_YAML)
	def should_load_from_file_with_specific_encoding(self):
		encoded_payload = 'Тест кодировок\n'
		self.fs.create_file('/data/filename.md', contents=(WITH_YAML + encoded_payload).encode('cp1251'))
		with self.assertRaises(UnicodeError):
			markdown.MarkdownFile(filename='/data/filename.md', encoding='utf-8')
		md = markdown.MarkdownFile(filename='/data/filename.md', encoding='utf-8', errors='replace')
		self.assertEqual(md.text, WITHOUT_YAML + '���� ���������\n')
		md = markdown.MarkdownFile(filename='/data/filename.md', encoding='cp1251')
		self.assertEqual(md.text, WITHOUT_YAML + encoded_payload)
	def should_convert_parsed_file_back_to_string(self):
		md = markdown.MarkdownFile(content=WITHOUT_YAML)
		self.assertEqual(str(md), WITHOUT_YAML)

		md = markdown.MarkdownFile(content=WITH_YAML)
		self.assertEqual(str(md), WITH_YAML)

		text = '---\nfirst: foo\nsecond: bar\n---\n\nSome text'
		md = markdown.MarkdownFile(content=text)
		self.assertEqual(str(md), text)
	def should_guess_title(self):
		md = markdown.MarkdownFile(content=WITH_YAML)
		self.assertEqual(md.get_title(), 'Note')

		md = markdown.MarkdownFile(content='---\nkey:value\n---\n' + WITHOUT_YAML)
		self.assertEqual(md.get_title(), 'heading')

		md = markdown.MarkdownFile(content='some content\n\n' + WITHOUT_YAML)
		self.assertEqual(md.get_title(), 'heading')

		md = markdown.MarkdownFile(content=WITHOUT_YAML)
		self.assertEqual(md.get_title(), 'heading')

		md = markdown.MarkdownFile(content='no heading', filename='/data/filename.md')
		self.assertEqual(md.get_title(), 'filename')

		md = markdown.MarkdownFile(content='no heading')
		self.assertIsNone(md.get_title())

RESULT_HTML = """\
<h1>heading</h1>
<p><strong>List</strong>:</p>
<ul>
<li>foo</li>
<li>bar</li>
</ul>"""

JINJA_CONTEXT = {
		'header' : 'heading',
		'list' : {
			'name' : 'List',
			'entries' : ['foo', 'bar'],
			},
		}

JINJA_TEMPLATE = """\
---
jinja_context_file: /data/context.json
---
# {{header}}

**{{list.name}}**:

{% for item in list.entries %}- {{item}}
{% endfor %}
"""

class TestMarkdownConversions(fs_unittest.TestCase):
	def setUp(self):
		self.setUpPyfakefs(modules_to_reload=[markdown])
		self.fs.create_dir('/data')
	def should_convert_markdown_to_html(self):
		md = markdown.MarkdownFile(content=WITH_YAML)
		self.assertEqual(md.to_html(), RESULT_HTML)
	def should_use_jinja_markup_if_requested(self):
		self.fs.create_file('/data/context.json', contents=json.dumps(JINJA_CONTEXT))
		md = markdown.MarkdownFile(content=JINJA_TEMPLATE)
		self.assertEqual(md.to_html(), RESULT_HTML)
