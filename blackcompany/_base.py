import bottle

def run(host='0.0.0.0', port=8080, debug=False, server_class=None):
	""" Runs web server on given host/port.
	"""
	kwargs = {}
	if server_class: # pragma: no cover
		kwargs['server'] = server_class
	while True:
		try:
			return bottle.run(host=host, port=port,
				quiet=not debug, debug=debug,
				reloader=False,
				**kwargs
				)
		except FileNotFoundError: # pragma: no cover -- Windows sometimes may interrupt bottle internal loop.
			continue

import click

def run_cli(host='0.0.0.0', port=8080): # pragma: no cover -- wrapper
	""" Creates CLI interface for webservice, can serve as entry point.

	Usage:

	if __name__ == '__main__':
		run_cli(...)
	"""
	@click.command()
	@click.option('--debug', is_flag=True, help='Shows debug output.')
	def cli(debug=False):
		run(host=host, port=port, debug=debug)
	return cli()
