"""Provides possibilities for sending commands to DoHome devices"""
# pylint: disable=no-name-in-module
from __future__ import annotations
from typing import Final
from socket import AF_INET, SOCK_DGRAM, socket, error
from json import dumps, loads
from logging import getLogger

_LOGGER = getLogger(__name__)

_API_PORT: Final = 6091
_COMMAND_PING: Final = "cmd=ping\r\n"
_BUFFER_SIZE: Final = 1024

_transport = socket(AF_INET, SOCK_DGRAM)
_transport.settimeout(0.5)


def _format_command(sid: str, cmd: int, data: dict) -> str:
    """Formats DoHome command string"""
    data["cmd"] = cmd
    return '&'.join([
        "cmd=ctrl",
        "devices={[" + sid + "]}"
        "op=" + dumps(data)
    ])


def _parse_entity(resp: str) -> dict:
    return resp.split("=")


def _parse_entities(resp: str) -> tuple[str, str]:
    return map(_parse_entity, resp.split('&'))


def _parse_response(resp: bytes) -> dict:
    """Parses DoHome response"""
    entities = _parse_entities(resp)
    return {
        entity[0]: entity[1] for entity in entities
    }


def _send_command(address: str, sid: str, cmd: int, data=None) -> dict | None:
    """Sends command to DoHome device"""
    if data is None:
        data = {}
    command = _format_command(sid, cmd, data)
    _LOGGER.debug('command to %s :%s', address, command)
    result = _send_raw_request(address, command)
    if result is None:
        return None
    return loads(_parse_response(result)['op'])


def _send_raw_request(address: str, req: str) -> dict | None:
    try:
        _transport.sendto(req.encode(), (address, _API_PORT))
        response, _ = _transport.recvfrom(_BUFFER_SIZE)
    except error:
        _LOGGER.debug("%s: error", address)
        return None
    if response is None:
        return None
    response_str = response.decode("utf-8")
    _LOGGER.debug("%s: response '%s'", address, response_str)
    return response_str


def _get_device_info(address: str) -> dict | None:
    return _parse_response(_send_raw_request(address, _COMMAND_PING))
