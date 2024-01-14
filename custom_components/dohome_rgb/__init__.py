"""DoHome Home Assistant integration"""
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
)

from .constants import DOMAIN


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Setup DoHome platform"""
    hass.async_create_task(
        async_load_platform(hass, "light", DOMAIN, {}, config)
    )
    return True
