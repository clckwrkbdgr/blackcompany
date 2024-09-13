from __future__ import absolute_import
from ._six import Path
import markdown
import markdown.extensions, markdown.preprocessors
import yaml, json
import jinja2
from . import dotdict

class MarkdownJinja(markdown.extensions.Extension):
	""" Inspired by: https://github.com/qzb/markdown-jinja/ """
	def __init__(self, params):
		self.config = {
				'params': [params, 'Default location of JSON file containing template context']
				}
	def extendMarkdown(self, md, *args):
		md.preprocessors.register(
				Preprocessor(md.parser, self.getConfigs()), 'jinja', 175,
				)

class Preprocessor(markdown.preprocessors.Preprocessor):
	""" Inspired by: https://github.com/qzb/markdown-jinja/ """
	def __init__(self, md, config):
		super(Preprocessor, self).__init__(md)
		self.environment = jinja2.Environment()
		self.context = config['params']
	def run(self, lines):
		text = '\n'.join(lines)
		template = self.environment.from_string(text)
		new_text = template.render(self.context)
		return new_text.splitlines()

class MarkdownFile(object):
	""" Represents markdown file with optional YAML header (separated by dash line '---').
	File should also start with this separator to indicate presense of YAML header:
	  ---
	  header: ...
	  ---
	  <content>
	Header and text are available through corresponding fields.
	If header is a dict (usually it should be), it is turned into dotdict.
	"""
	def __init__(self, filename=None, encoding=None, errors=None, content=None):
		""" Creates Markdown document either directly from content or from file.
		If filename is specified and content is not, reads content from the file.
		Parameters encoding and errors behave like in pathlib.Path.read_text().
		"""
		self.filename = Path(filename) if filename is not None else None
		if self.filename and not content:
			content = self.filename.read_text(encoding=encoding, errors=errors)
		self.header = {}
		self.text = content or ''
		self._parse_content(content or '')
	def _parse_content(self, content):
		if not content:
			return
		if not content.startswith('---\n'):
			return
		end_header = content.find('---\n', 1)
		if end_header < 0:
			return
		header = content[4:end_header]
		self.header = yaml.safe_load(header)
		if isinstance(self.header, dict):
			self.header = dotdict(self.header)
		self.text = content[end_header+4:]
	def __repr__(self): # pragma: no cover
		return 'MarkdownFile(filename={0}, text={1} chars)'.format(repr(self.filename), len(self.text))
	def __str__(self):
		header = self.header
		if not header:
			return self.text
		if isinstance(header, dict):
			header = dict(header)
		try:
			header = yaml.dump(header, default_flow_style=False, allow_unicode=True, sort_keys=False)
		except TypeError: # pragma: no cover -- dump_all() got an unexpected keyword argument 'sort_keys'
			header = yaml.dump(header, default_flow_style=False, allow_unicode=True)
		if not header.endswith('\n'): # pragma: no cover -- no real case.
			header += '\n'
		return '---\n' + header + '---\n' + self.text

	def get_title(self):
		""" Tries to guess title of the markdown document.
		If there is field .title in the YAML header, uses that.
		Otherwise tries to find first level-1 heading.
		If everything fails and filename is defined, uses its basename.
		"""
		if 'title' in self.header:
			return self.header['title']
		if self.text.startswith('# '):
			return self.text[2:self.text.find('\n')].strip()
		top_level_heading = self.text.find('\n# ')
		if top_level_heading > -1:
			top_level_heading += 3
			return self.text[top_level_heading:self.text.find('\n', top_level_heading)].strip()
		if self.filename:
			return self.filename.stem
		return None
	def to_html(self):
		""" Converts content to HTML.
		If 'jinja_context_file' is amongs headers, treats content as Jinja template
		and uses JSON object from file as parameters for the template.
		"""
		extensions = [
					'markdown.extensions.tables',
					'markdown.extensions.fenced_code',
				]
		if 'jinja_context_file' in self.header:
			jinja_context_file = Path(self.header['jinja_context_file'])
			if not jinja_context_file.is_absolute(): # pragma: no cover - TODO needs use-case and scenario. Forgot the original case.
				jinja_context_file = Path(self.filename).parent/jinja_context_file
			params = json.loads(jinja_context_file.read_text())
			extensions.append(MarkdownJinja(params))
		return markdown.markdown(self.text, extensions=extensions)
