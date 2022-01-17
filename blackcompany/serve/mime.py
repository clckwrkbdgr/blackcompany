import functools
from ._base import Endpoint

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
	def serve(self, route, filepath, decorator=None, path_param=None, on_remote_info=None, **params):
		""" Serves given file on given route as-is with current MIME type.
		If custom handler is defined for this MIME type, it is called instead,
		and all arguments are passed to the actual handler function.

		If path_param is given, it overrides path_param from custom().

		For all parameters see Endpoint class.

		All additional keyword arguments will be passed to Endpoint.serve() and eventually to a custom handler.
		"""
		content_type = '{0}/{1}'.format(self.type, self.subtype)
		custom_handler = self.root.handlers.get( (self.type, self.subtype) )

		endpoint = Endpoint(route, filepath,
				content_type=content_type,
				custom_handler=custom_handler,
				path_param=path_param,
				decorator=decorator, on_remote_info=on_remote_info,
				)
		endpoint.serve(**params)
	def custom(self, path_param=None):
		""" Decorator to register custom handler for current MIME type.

		Handler should be a function with at least two positional parameters: (route, filepath).
		For more documentation on defining handlers and processing path_param see Endpoint class.

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
