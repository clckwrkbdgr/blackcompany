class dotdict(dict):
	""" Dict that support dotted access:
	  d['value']['nested_value'] == d.value.nested_value

	<https://stackoverflow.com/a/23689767/2128769>
	"""
	def __getattr__(self, attr):
		value = dict.get(self, attr)
		return dotdict(value) if type(value) is dict else value
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__
	def __getstate__(self):
		return dict(self)
	def __setstate__(self, data):
		self.clear()
		self.update(data)
