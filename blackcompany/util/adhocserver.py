import threading
import six
from ..util import _six
import bottle
import pyfakefs.fake_filesystem_unittest as fs_unittest
from .. import _base

class StoppableServer(bottle.ServerAdapter):
	""" Server adapter that can be stopped remotely.
	Allows only one global instance which is available as StoppableServer.instance()
	Stops via StoppableServer.instance().shutdown()
	"""
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
		""" Waits until server is up. """
		while not self.started:
			continue
	def shutdown(self):
		""" Shuts server down. """
		if self.srv:
			self.srv.shutdown()
	@classmethod
	def instance(cls):
		""" Returns global instance.
		Will fail if instance is not initialized yet by bottle.
		"""
		while six.PY2 and not cls.instances: # pragma: no cover -- Py2 may reach here too soon.
			continue
		assert len(cls.instances) == 1, cls.instances
		return cls.instances[0]

def get_free_tcp_port():
	""" Tries to find first free network port.
	Prone to race conditions.
	"""
	import socket
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind(('', 0))
	addr, port = tcp.getsockname()
	tcp.close()
	return port

class AdhocBackgroundServer:
	""" Runs ad-hoc server in background thread and stops it on request.
	May be used as context manager.
	"""
	def __init__(self, hostname='localhost', port=None):
		""" Initializes server.
		If port is not given, tries to find the first one available.
		"""
		self.hostname = hostname
		self.port = port or get_free_tcp_port()
		self._service_thread = threading.Thread(target=_base.run, kwargs=dict(host=self.hostname, port=self.port, server_class=StoppableServer))
		self._service_thread.daemon = True
	def start(self):
		self._service_thread.start()
		StoppableServer.instance().wait_for_start()
	def stop(self):
		StoppableServer.instance().shutdown()
		self._service_thread.join()
	def __enter__(self):
		self.start()
		return self
	def __exit__(self, _1, _2, _3):
		self.stop()
