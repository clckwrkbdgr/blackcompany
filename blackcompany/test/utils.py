import threading
import six
from ..util import _six
import bottle
import pyfakefs.fake_filesystem_unittest as fs_unittest
from .. import _base

class StoppableServer(bottle.ServerAdapter):
	instances = []
	def __init__(self, *args, **kwargs):
		self.instances.append(self)
		self.srv = None
		self.started = False
		super(StoppableServer, self).__init__(*args, **kwargs)
	def run(self, handler): # pragma: no cover -- Copy-pasted from bottle source code just to have self.srv instance.
		from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
		from wsgiref.simple_server import make_server
		import socket

		class FixedHandler(WSGIRequestHandler):
			def address_string(self): # Prevent reverse DNS lookups please.
				return self.client_address[0]
			def log_request(*args, **kw):
				if not self.quiet:
					return WSGIRequestHandler.log_request(*args, **kw)

		handler_cls = self.options.get('handler_class', FixedHandler)
		server_cls  = self.options.get('server_class', WSGIServer)

		if ':' in self.host: # Fix wsgiref for IPv6 addresses.
			if getattr(server_cls, 'address_family') == socket.AF_INET:
				class server_cls(server_cls):
					address_family = socket.AF_INET6

		self.srv = make_server(self.host, self.port, handler, server_cls, handler_cls)
		self.started = True
		self.srv.serve_forever()
		self.instances.remove(self)
	def wait_for_start(self):
		while not self.started:
			continue
	def shutdown(self):
		if self.srv:
			self.srv.shutdown()
	@classmethod
	def instance(cls):
		while six.PY2 and not cls.instances: # pragma: no cover -- Py2 may reach here too soon.
			continue
		assert len(cls.instances) == 1, cls.instances
		return cls.instances[0]

def get_free_tcp_port():
	import socket
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind(('', 0))
	addr, port = tcp.getsockname()
	tcp.close()
	return port

class WebServerTestCase(fs_unittest.TestCase):
	LOCALHOST = '127.0.0.1'
	def setUp(self):
		self._port = get_free_tcp_port()
		self._service_thread = threading.Thread(target=_base.run, kwargs=dict(host=self.LOCALHOST, port=self._port, server_class=StoppableServer))
		self._service_thread.daemon = True
		self._service_thread.start()
		self.addCleanup(self.shutdown)
		StoppableServer.instance().wait_for_start()
	def _get_url(self, path):
		return 'http://{0}:{1}/{2}'.format(self.LOCALHOST, self._port, path.lstrip('/'))
	def _get(self, path, with_info=False):
		url = self._get_url(path)
		request = _six.Request(url)
		response = _six.urlopen(request)
		data = response.read()
		if with_info:
			data = data, _six._wrap_urllib_request_response_info(response.info())
		return data
	def _post(self, path, data):
		request = _six.Request(self._get_url(path), method='POST', data=data)
		response = _six.urlopen(request)
		data = response.read()
		return data
	def _put(self, path, data):
		request = _six.Request(self._get_url(path), method='PUT', data=data)
		response = _six.urlopen(request)
		data = response.read()
		return data
	def _delete(self, path):
		request = _six.Request(self._get_url(path), method='DELETE')
		response = _six.urlopen(request)
		data = response.read()
		return data
	def shutdown(self):
		StoppableServer.instance().shutdown()
		self._service_thread.join()
