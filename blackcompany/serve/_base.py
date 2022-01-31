import functools
from collections import namedtuple
import bottle
from ..util._six import Path
from ..util import net as netutil

class Endpoint:
	""" Serves given filepath on given route.
	If content_type is specified, it will be used for response, otherwise it will be deducted by bottle.
	If custom handler is defined, it is called instead,
	and all arguments are passed to the actual handler function.

	Custom handler should accept at least two positional arguments: (route, filepath).
	Route goes to bottle. It's up to handler how to process filepath.
	Handler can also accept any number of keyword arguments, which will be passed to it as-is from corresponding serve().

	Custom HTTP method can be specified. Default is 'GET'.
	If read_data is specified and is True, request data is read from input stream (usually for POST or PUT methods). By default is True for POST and PUT method, but can be explicitly specified as False.

	For parametrized routes pass last part of the path with param via path_param,
	the actual value will be added to filepath argument in handler's call,
	e.g.: route='/web/route' + path_param='<param_name>' => '/web/route/<param_name>', handler(route, filepath/<param_value>, ...)
	If path_param is specified (e.g. '<filename>'), route is treated as root
	for serving sub-entries. Path parameter will be added automatically,
	as well as actual subpath value will be added to the filepath parameter passed into the handler.

	If on_remote_info is not None, it should be a callable accepting RemoteInfo object. It will be called at the beginning of the handler.

	If decorator is not None, it is used to decorate actual bottle handler
	(should be a callable that takes function and returns a function).
	"""
	def __init__(self,
			route, filepath,
			custom_handler=None, method=None,
			read_data=None,
			content_type=None,
			path_param=None,
			decorator=None, on_remote_info=None,
			):
		self.route = route
		self.filepath = Path(filepath) if filepath else None
		self.content_type = content_type
		self.custom_handler = custom_handler
		self.method = method
		if read_data is None:
			read_data = self.method in ['POST', 'PUT']
		self.read_data = read_data
		self.path_param = path_param
		self.decorator = decorator
		self.on_remote_info = on_remote_info

		if not self.path_param and (self.custom_handler and self.custom_handler.path_param):
			self.path_param = self.custom_handler.path_param
		if self.path_param:
			if not self.route.endswith('/'):
				self.route += '/'
			if self.path_param.startswith('<') and self.path_param.endswith('>'):
				self.path_param = self.path_param[1:-1]
			self.route += '<{0}>'.format(self.path_param)
	def serve(self, **params):
		# Consolidate parameters for closure function
		# to prevent issues with not defined local variables.
		context = {
				'filepath' : self.filepath,
				'on_remote_info' : self.on_remote_info,
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
			if self.custom_handler:
				if self.path_param in bottle_handler_args:
					filepath = Path(filepath)/bottle_handler_args[self.path_param]
					del bottle_handler_args[self.path_param]
				kwargs = {}
				kwargs.update(bottle_handler_args)
				kwargs.update(params)
				data = filepath
				if self.read_data:
					data = bottle.request.body.read()
				return self.custom_handler(self.route, data, **kwargs)
			bottle.response.content_type = self.content_type
			return Path(filepath).read_bytes()

		if self.decorator:
			_actual = self.decorator(_actual)
		if self.method:
			bottle.route(self.route, method=self.method)(_actual)
		else:
			bottle.route(self.route)(_actual)
