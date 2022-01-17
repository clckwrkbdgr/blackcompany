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

def entry(route, api_handler):
	methods_without_data = 'get delete'.split()
	methods_with_data = 'post put'.split()
	for method, with_data in itertools.chain(zip(methods_without_data, itertools.repeat(False)), zip(methods_with_data, itertools.repeat(True))):
		if not hasattr(api_handler, method):
			continue
		endpoint = Endpoint(route, None, method=method.upper(), custom_handler=MethodHandler(getattr(api_handler, method), with_data=with_data))
		endpoint.serve()
