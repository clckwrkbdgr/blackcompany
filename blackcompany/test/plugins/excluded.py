import bottle

@bottle.route('/excluded-plugin-test')
def plugin_test():
	return "You aren't supposed to be here, you know."
