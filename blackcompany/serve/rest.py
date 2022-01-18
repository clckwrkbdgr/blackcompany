import itertools
from ._base import Endpoint

class MethodHandler:
	def __init__(self, handler_func, path_param=None, with_data=False):
		self.handler_func = handler_func
		self.path_param = path_param
		self.with_data = with_data
	def __call__(self, route, data, **kwargs):
		if self.with_data:
			return self.handler_func(data, **kwargs)
		return self.handler_func(**kwargs)

def entry(route, api_handler, **serve_params):
	""" Defines REST endpoint on given route with given handler object.
	Handler object may be of any class, but have at least on of methods defined:
	- get()
	- post(data)
	- put(data)
	- delete()
	New Endpoint() object will be created for every available method.
	Rest of parameters will be passed through to underlying Endpoint() objects.
	"""
	methods_without_data = 'get delete'.split()
	methods_with_data = 'post put'.split()
	for method, with_data in itertools.chain(zip(methods_without_data, itertools.repeat(False)), zip(methods_with_data, itertools.repeat(True))):
		if not hasattr(api_handler, method):
			continue
		endpoint = Endpoint(route, None, method=method.upper(), custom_handler=MethodHandler(getattr(api_handler, method), with_data=with_data), **serve_params)
		endpoint.serve()

def instance(route, **serve_params):
	""" Convenience decorator to mark class as REST API handler object.
	New instance will be created for this class and passed to rest.entry()
	along with other parameters.
	Instance will be available as <cls>._instance
	"""
	def _actual(cls):
		instance = cls()
		cls._instance = instance
		entry(route, instance, **serve_params)
		return cls
	return _actual
