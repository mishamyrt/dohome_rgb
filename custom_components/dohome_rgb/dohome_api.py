"""Provides possibilities for sending commands to DoHome devices"""
# pylint: disable=no-name-in-module
from socket import AF_INET, SOCK_DGRAM, socket
from json import dumps, loads
from logging import getLogger

_LOGGER = getLogger(__name__)

API_PORT = 6091

_transport = socket(AF_INET, SOCK_DGRAM)
_transport.settimeout(0.5)

def _format_command(sid: str, cmd: int, data: dict) -> str:
    """Formats DoHome command string"""
    data['cmd'] = cmd
    return '&'.join([
        'cmd=ctrl',
        'devices={[' + sid + ']}'
        'op=' + dumps(data)
    ])

def _parse_response(resp: str) -> dict:
    """Parses DoHome response"""
    data = {i.split('=')[0]:i.split('=')[1] for i in resp.decode('utf-8').split('&')}
    return loads(data['op'])

def _send_command(address: str, sid: str, cmd: int, data=None):
    """Sends command to DoHome device"""
    if data is None:
        data = {}
    command = _format_command(sid, cmd, data)
    _LOGGER.debug('command :%s', command)
    try:
        _transport.sendto(command.encode(), (address, API_PORT))
        data, _ = _transport.recvfrom(1024)
    # pylint: disable=bare-except
    except:
        _LOGGER.debug('Request error: %s', address)
        return None
    if data is None:
        return None
    _LOGGER.debug('result :%s', data.decode('utf-8'))
    return _parse_response(data)
