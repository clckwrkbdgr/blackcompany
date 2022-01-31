""" Custom layer for Py2/Py3 support. """

try:
	from pathlib2 import Path
except ImportError: # pragma: no cover
	from pathlib import Path

import functools
try:
	functools.lru_cache
except AttributeError: # pragma: no cover
	import backports.functools_lru_cache
	functools.lru_cache = backports.functools_lru_cache.lru_cache

import tempfile
try:
	tempfile.TemporaryDirectory
except AttributeError: # pragma: no cover
	import backports.tempfile
	tempfile.TemporaryDirectory = backports.tempfile.TemporaryDirectory

def _get_content_type_py2(self): # pragma: no cover
	return self.type

def _wrap_urllib_request_response_info(response_info): # pragma: no cover
	if not hasattr(response_info, 'get_content_type'):
		response_info.get_content_type = _get_content_type_py2.__get__(response_info)
	return response_info
