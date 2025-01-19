"""Support for DoHome RGB Lights"""
import asyncio.exceptions as aio_exceptions
from datetime import timedelta
from typing import Any

import homeassistant.helpers.config_validation as cv
import homeassistant.util.color as color_util
import voluptuous as vol
from dohome_api import DoHomeLightsBroadcast, NotEnoughException
from dohome_api.transport import DoHomeBroadcastTransport
from homeassistant import config_entries, core
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)

from .color_utils import kelvin_to_mired
from .constants import BULB_KELVIN_MAX, BULB_KELVIN_MIN, CONF_GATEWAY, CONF_SIDS, DOMAIN

SCAN_INTERVAL = timedelta(seconds=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SIDS): cv.ensure_list,
    vol.Required(CONF_GATEWAY): str
})

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up desk light."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    transport = DoHomeBroadcastTransport(data["gateway"])
    broadcast = DoHomeLightsBroadcast(data["sids"], transport)
    async_add_entities([DoHomeLightEntity(
        broadcast,
        data["info"]
    )])

class DoHomeLightEntity(LightEntity):
    """DoHome light entity"""

    # Constants attributes
    _attr_supported_color_modes = {ColorMode.RGB, ColorMode.BRIGHTNESS}
    _attr_min_color_temp_kelvin = BULB_KELVIN_MIN
    _attr_max_color_temp_kelvin = BULB_KELVIN_MAX

    # Initial state
    _color_mode = ColorMode.COLOR_TEMP
    _color_temp = 320
    _rgb = (0, 0, 0)
    _brightness = 200
    _is_on = False
    _available = False

    _light: DoHomeLightsBroadcast
    _info: dict
    _attr_name: str

    def __init__(self, light: DoHomeLightsBroadcast, info: dict) -> None:
        self._info = info
        self._light = light
        self._attr_name = f"{info["name"]} Light"

    @property
    def device_info(self):
        return self._info

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the color property."""
        return color_util.color_RGB_to_hs(*self._rgb)

    async def _update_state(self) -> None:
        try:
            state = await self._light.get_state()
        except (aio_exceptions.TimeoutError, aio_exceptions.CancelledError, NotEnoughException):
            self._attr_available = False
            return
        self._attr_available = True
        if not state["enabled"]:
            self._attr_is_on = False
            return
        self._attr_is_on = True
        if state["mode"] == "white":
            self._attr_color_mode = ColorMode.COLOR_TEMP
            self._attr_color_temp = state["mireds"]
            self._attr_brightness = state["brightness"]
        elif state["mode"] == "rgb" and self._rgb is None:
            self._attr_color_mode = ColorMode.HS
            self._attr_brightness = state["brightness"]
            self._rgb = tuple(state["rgb"])
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Reads state from the device"""
        if not await self._when_connected():
            self._attr_available = False
            return
        await self._update_state()


    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if ATTR_HS_COLOR in kwargs:
            self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
            self._attr_color_mode = ColorMode.HS
        elif ATTR_COLOR_TEMP_KELVIN in kwargs:
            self._attr_color_temp = kwargs[ATTR_COLOR_TEMP_KELVIN]
            self._attr_color_mode = ColorMode.COLOR_TEMP
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        if not await self._when_connected():
            return
        if self._attr_color_mode == ColorMode.COLOR_TEMP:
            await self._light.set_white(
                kelvin_to_mired(self._attr_color_temp),
                self._attr_brightness
            )
        else:
            await self._light.set_rgb(self._rgb, self._attr_brightness)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if await self._when_connected():
            await self._light.turn_off()

    async def _when_connected(self) -> bool:
        if not self._light.connected:
            try:
                await self._light.get_time()
                self._attr_available = True
            except (
                aio_exceptions.TimeoutError,
                aio_exceptions.CancelledError,
                NotEnoughException,
                IOError,
            ):
                self._attr_available = False
                return False
        return True
