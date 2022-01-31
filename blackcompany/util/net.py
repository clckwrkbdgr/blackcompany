import functools
from ..util import _six
import socket
from collections import namedtuple

RemoteInfo = namedtuple('RemoteInfo', 'ip name')

@functools.lru_cache()
def get_request_remote_info(remote_ip):
	remote_name = socket.getnameinfo((remote_ip, 0), 0)[0] if remote_ip else None
	return RemoteInfo(ip=remote_ip, name=remote_name)
