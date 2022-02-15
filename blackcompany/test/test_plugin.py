import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import os
from ..util import _six
from . import utils
from .. import _base
from .. import serve

serve.plugin.load(os.path.join(os.path.dirname(__file__), 'plugin.py'))
serve.plugin.discover(os.path.join(os.path.dirname(__file__), 'plugins'), pattern='*plugin*.py')

class TestPlugins(utils.WebServerTestCase):
	def setUp(self):
		super(TestPlugins, self).setUp()
		self.setUpPyfakefs(modules_to_reload=[_base, serve])
	def should_load_plugin(self):
		data = self._get('/plugin-test')
		self.assertEqual(data, b'Hello, world of plugins!')
	def should_discover_plugins_recursively(self):
		data = self._get('/main-plugin-test')
		self.assertEqual(data, b'Main plugin reports for duty!')

		data = self._get('/subplugin-test')
		self.assertEqual(data, b'Subplugin reports for duty!')

		with self.assertRaises(_six.HTTPError) as e:
			self._get('/excluded-plugin-test')
		self.assertEqual(e.exception.code, 404)
