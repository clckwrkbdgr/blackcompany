import bottle

@bottle.route('/main-plugin-test')
def plugin_test():
	return 'Main plugin reports for duty!'
