import functools
from collections import namedtuple
import bottle
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
from ..util import markdown as util_markdown

class MimeHandler:
	def __init__(self, handler_func, path_param=None):
		self.handler_func = handler_func
		self.path_param = path_param
	def __call__(self, *args, **kwargs):
		return self.handler_func(*args, **kwargs)

class MimeRoot:
	def __init__(self):
		self.handlers = {} # of MimeHandler
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
	def serve(self, route, filepath, decorator=None, **params):
		""" Serves given file on given route as-is with current MIME type.
		If custom handler is defined for this MIME type, it is called instead,
		and all arguments are passed to the actual handler function.

		If decorator is not None, it is used to decorate actual bottle handler
		(should be a callable that takes function and returns a function).
		"""
		content_type = '{0}/{1}'.format(self.type, self.subtype)
		custom_handler = self.root.handlers.get( (self.type, self.subtype) )

		if custom_handler and custom_handler.path_param:
			if not route.endswith('/'):
				route += '/'
			route += custom_handler.path_param

		def _actual(**bottle_handler_args):
			if custom_handler:
				kwargs = {}
				kwargs.update(bottle_handler_args)
				kwargs.update(params)
				return custom_handler(route, filepath, **kwargs)
			bottle.response.content_type = content_type
			return Path(filepath).read_bytes()

		if decorator:
			_actual = decorator(_actual)
		bottle.route(route)(_actual)
	def custom(self, path_param=None):
		""" Decorator to register custom handler for current MIME type.
		Handler should accept positional arguments: (route, filepath).
		Route goes to bottle. It's up to handler how to process filepath.
		Handler can also accept any number of keyword arguments, which will be passed to it as-is from corresponding serve().

		For parametrized routes pass last part of the path with param via path_param,
		the actual value will be added to keywords arguments in handler's call,
		e.g.: route='/web/route' + path_param='<param_name>' => '/web/route/<param_name>', handler(route, filepath, param_name=None, ...)

		NOTE: MIME type of actual outgoing response will be handled by bottle internally,
		so it may not be the same as the MIME of the file. E.g. markdown file (text/markdown) may be converted to and returned as text/html.

		@mime.Type.SubType.custom()
		def my_handler(route, filepath):
			return <response based on file...>
		"""
		def _actual(func):
			self.root.handlers[(self.type, self.subtype)] = MimeHandler(func, path_param=path_param)
			@functools.wraps(func)
			def _wrapper(route, filepath, **params):
				self.serve(route, filepath, **params)
			return _wrapper
		return _actual

mime = MimeRoot()

@mime.Directory.Static.custom(path_param='<filename>')
def static_content(route, rootdir, filename):
	""" Serves static content from given rootdir.
	Route should not include bottle variable:
	'/some/route/' to serve '/some/route/<filenames>'
	"""
	return bottle.static_file(str(filename), root=str(rootdir))

DirectoryListEntry = namedtuple('DirectoryListEntry', 'path name')

@mime.Directory.List.custom()
def directory_listing(route, rootdir, template_file=None, content_template_file=None):
	""" Serves html listing of given directory.
	Content is wrapped into given HTML template.
	Template should contain Jinja tags {{title}} and {% for entry in entries %} with {{entry.path}} and {{entry.name}}

	If content_template_file is given, then 'for' part should be defined there,
	and main template should contain tag {{!content}}
	"""
	if not route.endswith('/'):
		route += '/'
	entries = []
	for entry in sorted(Path(rootdir).iterdir()):
		entries.append(DirectoryListEntry(route + entry.name, entry.name))

	template_file = Path(template_file).read_text()
	params = {'entries' : entries}
	if content_template_file:
		content_template_file = Path(content_template_file).read_text()
		params['content'] = bottle.template(content_template_file, **params)
	return bottle.template(template_file, title='Index of {0}'.format(rootdir), **params)

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
