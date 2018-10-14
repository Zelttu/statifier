import os
import platform
import socket
from requests import get


def run(**args):
    print "[*] In system module."
    data = {}

    data['os'] = platform.system()
    data['ip'] = get('https://api.ipify.org').text
    data['local_ip'] = socket.gethostbyname(socket.gethostname())
    data['architecture'] = platform.architecture()[0]
    data['uname'] = " ".join(platform.uname())
    # Get Wifi / Ethernet

    return str(data)
