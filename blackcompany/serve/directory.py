from collections import namedtuple
try:
	from pathlib2 import Path
except: # pragma: no cover
	from pathlib import Path
import bottle
from ._base import mime
from .. import util

@mime.Directory.Static.custom(path_param='<filename>')
def static_content(route, rootpath, filename=None):
	""" Serves static content from given rootdir.
	Route should not include bottle variable:
	'/some/route/' to serve '/some/route/<filenames>'
	"""
	if not filename:
		rootpath, filename = rootpath.parent, rootpath.name
	return bottle.static_file(str(filename), root=str(rootpath))

DirectoryListEntry = namedtuple('DirectoryListEntry', 'path name')

@mime.Directory.List.custom()
def directory_listing(route, rootdir, template_file=None, content_template_file=None, title=None):
	""" Serves html listing of given directory.
	Content is wrapped into given HTML template.
	Template should contain Jinja tags {{title}} and {% for entry in entries %} with {{entry.path}} and {{entry.name}}

	If content_template_file is given, then 'for' part should be defined there,
	and main template should contain tag {{!content}}
	"""
	rootdir = Path(rootdir)
	title = title or 'Index of {0}'.format(rootdir.name)
	if not route.endswith('/'):
		route += '/'
	entries = []
	for entry in sorted(rootdir.iterdir()):
		entries.append(DirectoryListEntry(route + entry.name, entry.name))

	template_file = Path(template_file).read_text()
	params = {'entries' : entries}
	if content_template_file:
		content_template_file = Path(content_template_file).read_text()
		params['content'] = bottle.template(content_template_file, **params)
	return bottle.template(template_file, title=title, **params)
