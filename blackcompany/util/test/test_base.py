import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import pickle
from .. import _base
dotdict = _base.dotdict

class TestDotDict(unittest.TestCase):
	def should_access_dotdict_fields_via_dot(self):
		d = dotdict()
		d['field'] = 'foo'
		self.assertEqual(d.field, 'foo')
		self.assertEqual(d['field'], 'foo')
	def should_create_dotdict_from_base_dict(self):
		d = dotdict({'field':'foo'})
		self.assertEqual(d.field, 'foo')
		self.assertEqual(d['field'], 'foo')
	def should_set_dotdict_fields_via_dot(self):
		d = dotdict({'field':'foo'})
		d.field = 'foo'
		self.assertEqual(d.field, 'foo')
		self.assertEqual(d['field'], 'foo')
	def should_convert_nested_dicts_to_dotdicts(self):
		d = dotdict({'field':'foo', 'nested' : {'subfield': 'bar'}})
		self.assertEqual(d.field, 'foo')
		self.assertEqual(d.nested.subfield, 'bar')
	def should_pickle_and_unpickle_dotdict(self):
		d = dotdict({'field':'foo', 'nested' : {'subfield': 'bar'}})
		data = pickle.dumps(d)
		other = pickle.loads(data)
		self.assertEqual(d, other)
		self.assertTrue(type(other) is dotdict)
		self.assertTrue(type(other.nested) is dotdict)
