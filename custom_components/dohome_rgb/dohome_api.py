"""Provides possibilities for sending commands to DoHome devices"""
# pylint: disable=no-name-in-module
from __future__ import annotations
from socket import AF_INET, SOCK_DGRAM, socket, error
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
    data = {i.split('=')[0]: i.split('=')[1] for i in resp.decode('utf-8').split('&')}
    return loads(data['op'])


def _send_command(address: str, sid: str, cmd: int, data=None) -> dict | None:
    """Sends command to DoHome device"""
    if data is None:
        data = {}
    command = _format_command(sid, cmd, data)
    _LOGGER.debug('command to %s :%s', address, command)
    return _send_raw_request(address, command)

def _send_raw_request(address: str, req: str) -> dict | None:
    try:
        _transport.sendto(req.encode(), (address, API_PORT))
        response, _ = _transport.recvfrom(1024)
    except error:
        _LOGGER.debug('error on %s', address)
        return None
    if response is None:
        return None
    _LOGGER.debug('result from %s: %s', address, response.decode('utf-8'))
    return _parse_response(response)
