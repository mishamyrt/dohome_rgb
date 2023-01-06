"""Support for DoHome"""
import logging
from asyncio import Future
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
)
from dohome_api import DoHomeGateway

DOMAIN = 'dohome_rgb'
CONF_SIDS = 'sids'

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Setup DoHome platform"""
    hass.async_create_task(
        async_load_platform(hass, "light", DOMAIN, {}, config)
    )
    return True
