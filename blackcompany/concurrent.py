""" Import this module first line in the file to have concurrent web service.
	import blackcompany.concurrent
Defaul WSGI implementation used by Bottle does not allow concurrent service
so incoming requests stuck in queue.
"""
from gevent import monkey; monkey.patch_all()
from blackcompany import *
