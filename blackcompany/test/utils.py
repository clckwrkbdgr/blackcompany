import threading
import six
from ..util import _six
import bottle
import pyfakefs.fake_filesystem_unittest as fs_unittest
from .. import _base
from ..util import adhocserver

class WebServerTestCase(fs_unittest.TestCase):
	LOCALHOST = '127.0.0.1'
	def setUp(self):
		self._server = adhocserver.AdhocBackgroundServer(self.LOCALHOST)
		self._port = self._server.port
		self.addCleanup(self._server.stop)
		self._server.start()
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
