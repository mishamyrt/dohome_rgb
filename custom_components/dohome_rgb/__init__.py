"""DoHome Home Assistant integration"""
import homeassistant.helpers.config_validation as cv
from homeassistant.const import Platform
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
)

from .constants import DOMAIN

CONFIG_SCHEMA = cv.platform_only_config_schema(DOMAIN)
PLATFORMS = [Platform.LIGHT]

async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Setup DoHome platform"""
    hass.async_create_task(
        async_load_platform(hass, "light", DOMAIN, {}, config)
    )
    return True
