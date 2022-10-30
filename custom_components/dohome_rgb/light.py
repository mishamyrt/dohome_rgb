"""Support for DoHome RGB Lights"""
import logging
from datetime import timedelta
from typing import (Callable, Optional, Final, Any)
import homeassistant.util.color as color_util
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    COLOR_MODE_HS,
    COLOR_MODE_COLOR_TEMP,
    LightEntity,
)
from dohome_api import DoHomeGateway, DoHomeLight

from . import (
    CONF_SIDS,
    DOMAIN
)

# pylint: disable=unused-argument

SCAN_INTERVAL = timedelta(seconds=5)
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up DoHome light platform"""
    gateway = hass.data[DOMAIN]
    entities = []
    for sid in config[DOMAIN][CONF_SIDS]:
        entities.append(DoHomeLightEntity(hass, sid, gateway))
    async_add_entities(entities)

class DoHomeLightEntity(LightEntity):
    """DoHome light entity"""
    # Constants attributes
    _attr_supported_color_modes: Final = {COLOR_MODE_HS, COLOR_MODE_COLOR_TEMP}
    _attr_supported_features: Final = SUPPORT_BRIGHTNESS | SUPPORT_COLOR
    _attr_min_mireds = 166
    _attr_max_mireds = 400
    # State values
    _attr_color_mode = COLOR_MODE_HS
    _attr_brightness = 0
    _attr_color_temp = 166
    _attr_is_on = False
    _attr_available = False
    _rgb = None
    # Late init values
    _gateway = None
    _device: DoHomeLight = None
    _sid = ''
    _host = None

    def __init__(self, hass, sid: str, gateway: DoHomeGateway):
        self._gateway = gateway
        self._sid = sid

    @property
    def hs_color(self):
        """Return the color property."""
        return color_util.color_RGB_to_hs(*self._rgb)

    @property
    def unique_id(self) -> str:
        """Return the unique id of the device."""
        return 'dohome' + self._sid

    async def _when_connected(self) -> bool:
        if self._device is None or not self._device.connected:
            try:
                self._device = await self._gateway.add_light(self._sid)
            except IOError:
                self._attr_available = False
                return False
        return True

    async def async_update(self) -> None:
        """Reads state from the device"""
        if not await self._when_connected():
            self._attr_available = False
            return
        state = self._device.get_state()
        self._attr_available = True
        if not state["enabled"]:
            self._attr_is_on = False
            return
        self._attr_is_on = True
        if state["mode"] == "white":
            self._attr_color_mode = COLOR_MODE_COLOR_TEMP
            self._attr_color_temp = state["mireds"]
            self._attr_brightness = state["brightness"]
        elif state["mode"] == "rgb" and self._rgb is None:
            self._attr_color_mode = COLOR_MODE_HS
            self._attr_brightness = state["brightness"]
            self._rgb = tuple(state["rgb"])

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if ATTR_HS_COLOR in kwargs:
            self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
            self._attr_color_mode = COLOR_MODE_HS
        elif ATTR_COLOR_TEMP in kwargs:
            self._attr_color_temp = kwargs[ATTR_COLOR_TEMP]
            self._attr_color_mode = COLOR_MODE_COLOR_TEMP
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        if not await self._when_connected():
            return
        if self._attr_color_mode == COLOR_MODE_COLOR_TEMP:
            await self._device.set_white(
                self._attr_color_temp,
                self._attr_brightness
            )
        else:
            await self._device.set_rgb(*self._rgb, self._attr_brightness)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if await self._when_connected():
            await self._device.set_enabled(False)
