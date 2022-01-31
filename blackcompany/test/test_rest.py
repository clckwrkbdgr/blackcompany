import sys, socket
import functools
import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
from ..util._six import Path
import bottle
from . import utils
from .. import serve

def track_user_agent(func):
	@functools.wraps(func)
	def _actual(*args, **kwargs):
		track_user_agent.history.append(bottle.request.get_header('User-Agent'))
		return func(*args, **kwargs)
	return _actual
track_user_agent.history = []

def track_remote_addr(remote_info):
	track_remote_addr.history.append(remote_info)
track_remote_addr.history = []

class CounterAPI:
	def __init__(self):
		self.counter = 1
	def get(self):
		return str(self.counter)
	def put(self, body):
		self.counter += int(body.decode())
	def post(self, body):
		self.counter = int(body.decode())
	def delete(self):
		self.counter = 0

counter_api_entry = CounterAPI()
serve.rest.entry('/api/counter', counter_api_entry, decorator=track_user_agent, on_remote_info=track_remote_addr)

@serve.rest.instance('/api/clipboard')
class ClipboardAPI:
	def __init__(self):
		self.value = ''
	def get(self):
		return str(self.value)
	def post(self, body):
		self.value = body.decode()

class TestREST(utils.WebServerTestCase):
	def setUp(self):
		super(TestREST, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[serve])

	def should_get_state(self):
		data = self._get('/api/counter')
		self.assertEqual(data, str(counter_api_entry.counter).encode())
	def should_post_new_state(self):
		self._post('/api/counter', b'666')
		data = self._get('/api/counter')
		self.assertEqual(data, b'666')
	def should_update_current_state(self):
		old_data = int(self._get('/api/counter').decode())
		self._put('/api/counter', b'1')
		new_data = int(self._get('/api/counter').decode())
		self.assertEqual(new_data, old_data + 1)
	def should_reset_current_state(self):
		self._delete('/api/counter')
		new_data = self._get('/api/counter')
		self.assertEqual(new_data, b'0')

	def should_get_state_on_limited_method_set(self):
		ClipboardAPI._instance.value = 'foo bar'
		data = self._get('/api/clipboard')
		self.assertEqual(data, b'foo bar')
	def should_post_new_state_on_limited_method_set(self):
		self._post('/api/clipboard', b'hello world')
		self.assertEqual(ClipboardAPI._instance.value, 'hello world')

	def should_call_custom_decorator(self):
		track_user_agent.history.clear()
		data = self._get('/api/counter')
		self.assertEqual(track_user_agent.history, ['Python-urllib/{0}.{1}'.format(*(sys.version_info[:2]))])

		track_user_agent.history.clear()
		data = self._post('/api/counter', b'100')
		self.assertEqual(track_user_agent.history, ['Python-urllib/{0}.{1}'.format(*(sys.version_info[:2]))])
	def should_track_remote_info(self):
		current_ip = self.LOCALHOST
		current_name = socket.getnameinfo((current_ip, 0), 0)[0]

		track_remote_addr.history.clear()
		data = self._get('/api/counter')
		self.assertEqual(track_remote_addr.history, [serve.RemoteInfo(current_ip, current_name)])

		track_remote_addr.history.clear()
		data = self._post('/api/counter', b'100')
		self.assertEqual(track_remote_addr.history, [serve.RemoteInfo(current_ip, current_name)])
