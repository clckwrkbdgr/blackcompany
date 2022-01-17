import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
import bottle
from . import utils
from .. import serve

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
serve.rest.entry('/api/counter', counter_api_entry)

class GetPostOnlyAPI:
	def __init__(self):
		self.value = ''
	def get(self):
		return str(self.value)
	def post(self, body):
		self.value = body.decode()

clip_api_entry = GetPostOnlyAPI()
serve.rest.entry('/api/clipboard', clip_api_entry)

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
		clip_api_entry.value = 'foo bar'
		data = self._get('/api/clipboard')
		self.assertEqual(data, b'foo bar')
	def should_post_new_state_on_limited_method_set(self):
		self._post('/api/clipboard', b'hello world')
		self.assertEqual(clip_api_entry.value, 'hello world')
