import os
from ..util._six import Path

def load(plugin_path):
	""" Load specified Python file as web server plugin. """
	module_spec = str(plugin_path)
	module_filename = module_spec
	module_name = os.path.basename(os.path.splitext(module_spec)[0])
	try: # pragma: no cover
		import importlib.util
		spec = importlib.util.spec_from_file_location(module_name, module_filename)
		module_instance = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module_instance)
	except AttributeError: # pragma: no cover
		from importlib.machinery import SourceFileLoader
		module_instance = SourceFileLoader(module_name, module_filename).load_module()
	except ImportError: # pragma: no cover
		import imp
		module_instance = imp.load_source(module_name, module_filename)

def discover(rootpath, pattern='*.py'):
	""" Discover and load available plugins in given rootdir (recursively).
	By default loads all found Python files, but wildcard pattern can be passed to include only specific files.
	"""
	for entry in Path(rootpath).glob('**/' + str(pattern)):
		load(entry)
