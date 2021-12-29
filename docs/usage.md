Usage
=====

Basic setup
-----------

```python
import blackcompany
```

or (for concurrent web service), as the very first line of the file:

```python
import blackcompany.concurrent
...
import blackcompany
# or even:
import blackcompany.concurrent as blackcompany
```

The line with `concurrent` should be the very first code line in the file.
It uses `gevent` monkey-patch mechanism to provide concurrency for the stdlib modules.

Running server
--------------

To have CLI runner define at the bottom of the main file:

```python
if __name__ == '__main__'
	blackcompany.run_cli(host=..., port=...)
```

Now it could be run from command line:

```bash
$ python -m mywebserver [--debug] ...
```

Defining endpoints
------------------

Blackcompany is build upon `bottle.py` and starts `bottle` server, so any `@bottle` definition should work without issues, e.g.:

```python
@bottle.route('/')
def index():
	return bottle.template('/home/user/web/index.html')
```

Module `blackcompany.serve` provides global object `blackcompany.serve.mime` which allows to define endpoints based on MIME type of the served file:

```python
mime.Image.PNG.serve('/images/favicon.png', '/home/user/web/favicon.png')
mime.Text.Plain.serve('/robots.txt', '/home/user/web/robots.txt')
```

Custom handler may be defined for MIME endpoint class, and then used to serve specific endpoints. Each handler should accept at least pair of arguments: `route, filepath`. Additional user-defined arguments are allowed as kwargs. They are passed directly from each endpoint definition.

```python
@mime.Text.Html.custom()
def my_html(route, filename, template_name=None):
	return bottle.template(find_template(template_name), body=Path(filename).read_text())

mime.Text.Html.serve('/faq', '/home/user/web/faq.html', template_name='faq')
mime.Text.Html.serve('/about', '/home/user/web/about.html', template_name='about')
```

Some pre-defined handlers exist for `Text.Markdown`, `Text.Html` etc.

There is a special predefined pseudo-MIME type `Directory`. It has several subtype handlers for directories:

- `Directory.Static` - serve static content from given directory. Uses `bottle.static_file` underneath.
- `Directory.List` - simple HTML templated index of a directory.

To serve content of some directory with custom MIME handler, define route with argument `path_param`:

```python
# E.g. /docs/index.md will fetch /home/user/web/docs/index.md and convert it to HTML.
mime.Text.Markdown.serve('/docs', '/home/user/web/docs', path_param='filename', template_file='/home/user/web/template.html')
```

See API help for more details.

Extra utils
-----------

- `blackcompany.utils.markdown.MarkdownFile`: handy class to work with Markdown files with YAML headers.
