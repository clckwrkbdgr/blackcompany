""" Import this module first line in the file to have concurrent web service.
	import blackcompany.concurrent
Defaul WSGI implementation used by Bottle does not allow concurrent service
so incoming requests stuck in queue.
"""
try:
	from gevent import monkey; monkey.patch_all()
except ImportError:
	import sys
	sys.stderr.write('Module "gevent" is not found.\n')
	sys.stderr.write('Bottle.py service will be accepting requests into single queue.\n')
	sys.stderr.write('(it may result in bad performan on loaded systems).\n')
	sys.stderr.write('Install module "gevent" to make service concurrent:\n')
	sys.stderr.write('  pip install gevent\n')
	sys.stderr.flush()
from blackcompany import *
