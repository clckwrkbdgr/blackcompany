from ..util._six import Path
import bottle
from . import mime
from ..util import markdown as util_markdown

@mime.Text.Html.custom()
def html(route, filename):
	""" Serves ready HTML file. """
	return bottle.template(Path(filename).read_text())

@mime.Text.Markdown.custom()
def markdown(route, filename, template_file, encoding=None):
	""" Serves markdown file, formatting it into given HTML Jinja template file.
	Template should contain Jinja tags {{title}} and {{!content}}
	"""
	md = util_markdown.MarkdownFile(filename=filename, encoding=encoding, errors='replace' if encoding else None)
	return bottle.template(Path(template_file).read_text(), title=md.get_title(), content=md.to_html())

@mime.Text.Plain.custom()
def plain_text(route, filename):
	""" Serves plain text file as-is. """
	return Path(filename).read_text()
