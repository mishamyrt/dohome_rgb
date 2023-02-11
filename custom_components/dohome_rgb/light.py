"""Support for DoHome RGB Lights"""
import logging
from datetime import timedelta
import asyncio.exceptions as aioexc
from typing import (
    Callable,
    Optional,
    Final,
    Any,
    Tuple,
    List
)
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    COLOR_MODE_HS,
    COLOR_MODE_COLOR_TEMP,
    PLATFORM_SCHEMA,
    LightEntity,
)
import homeassistant.util.color as color_util
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from dohome_api import DoHomeLightsBroadcast, DoHomeGateway, NotEnoughException
from . import CONF_SIDS

# pylint: disable=unused-argument,too-many-instance-attributes

SCAN_INTERVAL = timedelta(seconds=10)
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SIDS): cv.ensure_list
})

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up DoHome light platform"""
    if CONF_SIDS in config:
        gateway = DoHomeGateway()
        device = gateway.add_lights(config[CONF_SIDS])
        async_add_entities([
            DoHomeLightEntity(hass, config[CONF_SIDS], device)
        ])

class DoHomeLightEntity(LightEntity):
    """DoHome light entity"""

    # Constants attributes
    _attr_supported_color_modes: Final[set[str]] = {
        COLOR_MODE_HS,
        COLOR_MODE_COLOR_TEMP,
    }
    _attr_min_mireds: Final = 166
    _attr_max_mireds: Final = 400
    # State values
    _attr_color_mode: str = COLOR_MODE_COLOR_TEMP
    _attr_brightness: int = 200
    _attr_color_temp: int = 320
    _attr_is_on: bool = False
    _attr_available: bool = False
    _rgb: Tuple[int, int, int] = None
    # Late init values
    _device: DoHomeLightsBroadcast
    _sids: List[str]

    def __init__(self, hass, sids: List[str], device: DoHomeLightsBroadcast) -> None:
        self._device = device
        self._sids = sids

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the color property."""
        return color_util.color_RGB_to_hs(*self._rgb)

    @property
    def unique_id(self) -> str:
        """Return the unique id of the device."""
        return '-'.join(self._sids)

    async def async_update(self) -> None:
        """Reads state from the device"""
        if not await self._when_connected():
            self._attr_available = False
            return
        try:
            state = await self._device.get_state()
        except (aioexc.TimeoutError, aioexc.CancelledError, NotEnoughException):
            self._attr_available = False
            return
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
            await self._device.set_rgb(self._rgb, self._attr_brightness)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if await self._when_connected():
            await self._device.turn_off()

    async def _when_connected(self) -> bool:
        if not self._device.connected:
            try:
                await self._device.get_time()
                self._attr_available = True
            except (
                aioexc.TimeoutError,
                aioexc.CancelledError,
                NotEnoughException,
                IOError,
            ):
                self._attr_available = False
                return False
        return True
