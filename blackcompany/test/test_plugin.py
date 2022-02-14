import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import os
from . import utils
from .. import _base
from .. import serve

serve.plugin.load(os.path.join(os.path.dirname(__file__), 'plugin.py'))

class TestPlugins(utils.WebServerTestCase):
	def setUp(self):
		super(TestPlugins, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[_base, serve])
	def should_load_plugin(self):
		data = self._get('/plugin-test')
		self.assertEqual(data, b'Hello, world of plugins!')
