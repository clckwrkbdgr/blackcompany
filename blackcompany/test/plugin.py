import bottle

@bottle.route('/plugin-test')
def plugin_test():
	return 'Hello, world of plugins!'
