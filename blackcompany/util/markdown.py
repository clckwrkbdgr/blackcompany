from __future__ import absolute_import
try:
	from pathlib2 import Path
except ImportError: # pragma: no cover
	from pathlib import Path
import markdown
import yaml
from clckwrkbdgr.collections import dotdict

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
	def __init__(self, filename=None, content=None):
		self.filename = Path(filename) if filename is not None else None
		if self.filename and not content:
			content = self.filename.read_text()
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
		header = yaml.dump(header, default_flow_style=None)
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
