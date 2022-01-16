import functools
from collections import namedtuple
import bottle
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
from ..util import net as netutil

RemoteInfo = netutil.RemoteInfo

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

		If path_param is specified (e.g. '<filename>'), route is treated as root
		for serving sub-entries. Path parameter will be added automatically,
		as well as actual subpath value will be added to the filepath parameter passed into the handler.
		Overrides path_param from custom().

		If on_remote_info is not None, it should be a callable accepting RemoteInfo object. It will be called at the beginning of the handler.

		If decorator is not None, it is used to decorate actual bottle handler
		(should be a callable that takes function and returns a function).
		"""
		content_type = '{0}/{1}'.format(self.type, self.subtype)
		custom_handler = self.root.handlers.get( (self.type, self.subtype) )

		if not path_param and (custom_handler and custom_handler.path_param):
			path_param = custom_handler.path_param
		if path_param:
			if not route.endswith('/'):
				route += '/'
			if path_param.startswith('<') and path_param.endswith('>'):
				path_param = path_param[1:-1]
			route += '<{0}>'.format(path_param)

		# Consolidate parameters for closure function
		# to prevent issues with not defined local variables.
		context = {
				'filepath' : filepath,
				'on_remote_info' : on_remote_info,
				}
		def _actual(**bottle_handler_args):
			filepath = context['filepath']
			if context['on_remote_info'] is not None:
				try:
					remote_addr = bottle.request.headers.get('HTTP_X_FORWARDED_FOR') or bottle.request.headers.get('HTTP_REMOTE_ADDR') or bottle.request.headers.get('REMOTE_ADDR') or bottle.request.remote_addr
					remote_info = netutil.get_request_remote_info(remote_addr)
					context['on_remote_info'](remote_info)
				except: # pragma: no cover
					import traceback
					traceback.print_exc()
			if custom_handler:
				if path_param in bottle_handler_args:
					filepath = Path(filepath)/bottle_handler_args[path_param]
					del bottle_handler_args[path_param]
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
		the actual value will be added to filepath argument in handler's call,
		e.g.: route='/web/route' + path_param='<param_name>' => '/web/route/<param_name>', handler(route, filepath/<param_value>, ...)
		See more details in documentation for serve().

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
