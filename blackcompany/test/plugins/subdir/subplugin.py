import bottle

@bottle.route('/subplugin-test')
def plugin_test():
	return 'Subplugin reports for duty!'
