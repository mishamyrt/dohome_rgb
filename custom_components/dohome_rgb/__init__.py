"""Support for DoHome"""
import socket
import json
import logging
import struct
import platform
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from dohome_api import DoHomeGateway

DOMAIN = 'dohome_rgb'
CONF_SID = 'sid'
CONF_GATEWAY = 'gateway_ip'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_GATEWAY, default=None): cv.string
    })
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)
# _LOGGER.setLevel('DEBUG')

async def async_setup(hass, config):
    """Setup DoHome platform"""
    hass.data[DOMAIN] = DoHomeGateway(config[DOMAIN][CONF_GATEWAY])
    hass.async_create_task(
        async_load_platform(hass, "light", DOMAIN, {}, config)
    )
    return True
