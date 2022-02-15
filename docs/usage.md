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

Server plugins
--------------

Any Python file may be loaded as a server plugin. All service definitions in these files (either blackcompany or plain bottle endpoints) will be loaded as usual and accessible at the server.

```python
# /path/to/plugin.py
import bottle

@bottle.route('/plugin-endpoint')
def plugin_endpoint():
	return ...
```

```python
import blackcompany.serve
blackcompany.serve.plugin.load('/path/to/plugin.py')
```

It is also possible to discover and load plugins recursively:

```python
import blackcompany.serve
blackcompany.serve.plugin.discover('/root/path/of/plugins/', pattern='plugin_*.py')
```

REST API
--------

Simple REST API endpoints are defined using `blackcompany.serve.rest.entry()` with handler object that supports methods `get`, `post`, `put`, `delete`.

Example:

```python
class MyAPI:
	def get(self):
		...
	def put(self, body):
		...
	def post(self, body):
		...
	def delete(self):
		...

api_object = MyAPI()
blackcompany.serve.rest.entry('/api/path', api_object)
```

or, for convenience (if there assumed to be only one instance of the handler class):

```python
@blackcompany.serve.rest.entry('/api/path')
class MyAPI:
	def get(self):
		...
	...
```

Methods that are not implemented in handler object will be ignored when setting up route for the endpoint.
Object may implement any kind of internal state. Except for four predefined methods, there is no further restriction on method names.
Body passed to `PUT` and `POST` handlers will be a bytes object.

Git
---

Git repo can be served using following endpoint:

```python
blackcompany.serve.vcs.git_repo('/gitrepo', '/path/to/repo/root')
```

```sh
$ git clone http://localhost:8080/gitrepo .
```

**NOTE**: It is in very experimental state and some functions may not be working properly yet.

Extra utils
-----------

- `blackcompany.utils.markdown.MarkdownFile`: handy class to work with Markdown files with YAML headers.
