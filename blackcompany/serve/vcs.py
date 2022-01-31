from ._base import Endpoint
from ..util._six import Path
import bottle
from ..util import gitHttpBackend

class GitHTTPBackend:
	""" WSGI git-http-backend interface to actual endpoints.
	"""
	def __init__(self, route, repo_root):
		self.route = route
		self.repo_root = Path(repo_root)
	def get(self, path):
		return self._serve(path)
	def post(self, path):
		return self._serve(path)
	def _serve(self, path):
		git_project_root = self.repo_root
		git_dir = git_project_root/'.git'
		if not git_dir.exists() and (git_project_root/'HEAD').exists():
			git_dir = git_project_root
		git_info = git_dir/'info'
		if path == 'sparse-checkout' or (git_info/path).exists():
			return bottle.static_file(path, root=str(git_info))
		webroot = self.route
		environ = dict(bottle.request.environ)
		environ['PATH_INFO'] = environ['PATH_INFO'][len(webroot):]
		status_line, headers, response_body_generator = gitHttpBackend.wsgi_to_git_http_backend(environ, str(git_project_root))
		response = bottle.Response(response_body_generator, status_line, headers)
		bottle.response.content_type = response.get_header('Content-Type')
		return response

class MethodHandler:
	def __init__(self, handler_func, path_param):
		self.handler_func = handler_func
		self.path_param = path_param
	def __call__(self, route, _data, path, **kwargs):
		return self.handler_func(path, **kwargs)

def git_repo(route, repo_root, **serve_params):
	""" Defines Git repo endpoint on given route with given root.

	Endpoint() objects will be created for GET and POST.
	Rest of parameters will be passed through to underlying Endpoint() objects.
	"""
	backend = GitHTTPBackend(route, repo_root)

	get_endpoint = Endpoint(route, None, method='GET', custom_handler=MethodHandler(backend.get, 'path:path'), **serve_params)
	get_endpoint.serve()

	post_endpoint = Endpoint(route, None, method='POST', custom_handler=MethodHandler(backend.post, 'path:path'), read_data=False, **serve_params)
	post_endpoint.serve()
