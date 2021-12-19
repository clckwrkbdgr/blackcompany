import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import threading
from six.moves import urllib
import bottle

from . import utils
from .. import _base

@bottle.route('/test')
def test_page():
	return 'Hello, world!'

class TestWebService(unittest.TestCase):
	LOCALHOST = '127.0.0.1'
	def setUp(self):
		self._port = utils.get_free_tcp_port()
		self._service_thread = threading.Thread(target=_base.run, kwargs=dict(host=self.LOCALHOST, port=self._port, server_class=utils.StoppableServer))
		self._service_thread.daemon = True
		self._service_thread.start()
		utils.StoppableServer.instance().wait_for_start()
	def _get_url(self, path):
		return 'http://{0}:{1}/{2}'.format(self.LOCALHOST, self._port, path.lstrip('/'))
	def _get(self, path):
		req = urllib.request.urlopen(self._get_url('/test'))
		data = req.read()
		return data
	def tearDown(self):
		utils.StoppableServer.instance().shutdown()

	def should_run_service(self):
		data = self._get('/test')
		self.assertEqual(data, b'Hello, world!')

