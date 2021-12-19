import bottle

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
	def wait_for_start(self):
		while not self.started:
			continue
	def shutdown(self):
		if self.srv:
			self.srv.shutdown()
	@classmethod
	def instance(cls):
		assert len(cls.instances) == 1
		return cls.instances[0]

def get_free_tcp_port():
	import socket
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind(('', 0))
	addr, port = tcp.getsockname()
	tcp.close()
	return port

