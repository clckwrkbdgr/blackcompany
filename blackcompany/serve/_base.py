import functools
import bottle
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
from ..util import markdown as util_markdown

class MimeRoot:
	def __init__(self):
		self.handlers = {}
	def __getattr__(self, mime_type):
		return MimeType(self, mime_type.lower())

class MimeType:
	def __init__(self, root, mime_type):
		self.root, self.type = root, mime_type
	def __getattr__(self, mime_subtype):
		return MimeSubType(self.root, self.type, mime_subtype.lower())

class MimeSubType:
	def __init__(self, root, mime_type, mime_subtype):
		self.root, self.type, self.subtype = root, mime_type, mime_subtype
	def serve(self, route, filename, **params):
		""" Serves given file on given route as-is with current MIME type. """
		content_type = '{0}/{1}'.format(self.type, self.subtype)
		custom_handler = self.root.handlers.get( (self.type, self.subtype) )

		@bottle.route(route)
		def _actual():
			if custom_handler:
				return custom_handler(route, filename, **params)
			bottle.response.content_type = content_type
			return Path(filename).read_bytes()
	def custom(self):
		""" Decorator to register custom handler for current MIME type.

		NOTE: MIME type of actual outgoing response will be handled by bottle internally,
		so it may not be the same as the MIME of the file. E.g. markdown file (text/markdown) may be converted to and returned as text/html.

		@mime.Type.SubType.custom()
		def my_handler(route, filename):
			return <response based on file...>
		"""
		def _actual(func):
			self.root.handlers[(self.type, self.subtype)] = func
			@functools.wraps(func)
			def _wrapper(route, filename, **params):
				self.serve(route, filename, **params)
			return _wrapper
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

@mime.Text.Html.custom()
def html(route, filename):
	""" Serves ready HTML file. """
	return bottle.template(Path(filename).read_text())

@mime.Text.Markdown.custom()
def markdown(route, filename, template_file):
	""" Serves markdown file, formatting it into given HTML Jinja template file.
	Template should contain Jinja tags {{title}} and {{!content}}
	"""
	md = util_markdown.MarkdownFile(filename=filename)
	return bottle.template(Path(template_file).read_text(), title=md.get_title(), content=md.to_html())

@mime.Text.Plain.custom()
def plain_text(route, filename):
	""" Serves plain text file as-is. """
	return Path(filename).read_text()
