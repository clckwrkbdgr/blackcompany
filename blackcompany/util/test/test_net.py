import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import socket
from .. import net

class TestRemoteInfo(unittest.TestCase):
	LOCALHOST = '127.0.0.1'
	def should_get_remote_info_for_remote_addr(self):
		current_ip = self.LOCALHOST
		current_name = socket.getnameinfo((current_ip, 0), 0)[0]
		self.assertEqual(net.get_request_remote_info.__wrapped__(current_ip), net.RemoteInfo(current_ip, current_name))
