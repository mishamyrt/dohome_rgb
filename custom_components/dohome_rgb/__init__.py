"""DoHome Home Assistant integration"""
import voluptuous as vol
from homeassistant.const import CONF_PLATFORM
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
)

from .constants import DOMAIN

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): 'dohome_rgb',
    vol.Required('sids'): vol.All(cv.ensure_list, [cv.string])
})

CONFIG_SCHEMA = vol.Schema({
    'light': vol.All(cv.ensure_list, [PLATFORM_SCHEMA])
})

async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Setup DoHome platform"""
    hass.async_create_task(
        async_load_platform(hass, "light", DOMAIN, {}, config)
    )
    return True
