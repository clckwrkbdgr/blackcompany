import bottle
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
from ..util import markdown as util_markdown

class MimeRoot:
	def __getattr__(self, mime_type):
		return MimeType(mime_type)

class MimeType:
	def __init__(self, mime_type):
		self.type = mime_type
	def __getattr__(self, mime_subtype):
		return MimeSubType(self.type, mime_subtype)

class MimeSubType:
	def __init__(self, mime_type, mime_subtype):
		self.type, self.subtype = mime_type, mime_subtype
	def serve(self, route, filename):
		content_type = '{0}/{1}'.format(self.type, self.subtype)

		@bottle.route(route)
		def _actual():
			bottle.response.content_type = content_type
			return Path(filename).read_bytes()
		return _actual

mime = MimeRoot()

def static_content(route, rootdir):
	""" Serves static content from given rootdir.
	Route should not include bottle variable:
	'/some/route/' to serve '/some/route/<filenames>'
	"""
	if not route.endswith('/'):
		route += '/'
	@bottle.route(route + '<filename>')
	def _actual(filename):
		return bottle.static_file(str(filename), root=str(rootdir))
	return _actual

def html(route, filename):
	""" Serves ready HTML file. """
	@bottle.route(route)
	def _actual():
		return bottle.template(Path(filename).read_text())

def markdown(route, filename, template_file):
	""" Serves markdown file, formatting it into given HTML Jinja template file.
	Template should contain Jinja tags {{title}} and {{!content}}
	"""
	@bottle.route(route)
	def _actual():
		md = util_markdown.MarkdownFile(filename=filename)
		return bottle.template(Path(template_file).read_text(), title=md.get_title(), content=md.to_html())

def plain_text(route, filename):
	""" Serves plain text file as-is. """
	@bottle.route(route)
	def _actual():
		return Path(filename).read_text()
