"""Support for DoHome RGB Lights"""
import asyncio
from datetime import timedelta
from typing import Any

import homeassistant.util.color as color_util
import voluptuous as vol
from dohome_api import doit
from dohome_api.device import KELVIN_MAX, KELVIN_MIN, DoHomeDevice, LightMode
from dohome_api.exc import DoHomeException
from homeassistant import config_entries, core
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.helpers.entity import DeviceInfo

from .constants import CONF_DEVICE, CONF_HOST, CONF_INFO, DOMAIN

SCAN_INTERVAL = timedelta(seconds=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_INFO): dict,
    vol.Required(CONF_HOST): str
})

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up desk light."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([DoHomeLightEntity(
        data[CONF_DEVICE],
        data[CONF_INFO],
        config_entry.entry_id,
    )])

class DoHomeLightEntity(LightEntity):
    """DoHome light entity"""

    # Constants attributes
    _attr_supported_color_modes = {ColorMode.HS, ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = KELVIN_MIN
    _attr_max_color_temp_kelvin = KELVIN_MAX

    # Initial state
    _color_mode = ColorMode.COLOR_TEMP
    _color_temp = 3500
    _rgb = (0, 0, 0)
    _brightness = 255
    _is_on = False
    _available = False

    _device: DoHomeDevice
    _info: doit.DeviceInfo
    _attr_name: str

    def __init__(self, device: DoHomeDevice, info: doit.DeviceInfo, entry_id: str) -> None:
        self._entry_id = entry_id
        self._info = info
        self._device = device
        self._attr_name = f"DoHome {info['sid']}"
        self._attr_unique_id = info["mac"]

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._info["mac"])
            },
            name=self.name,
            model=f'{self._info["type"]} {self._info["chip"]}',
            sw_version="1.1.0"
        )

    @property
    def color_mode(self) -> ColorMode:
        return self._color_mode

    @property
    def color_temp_kelvin(self) -> int:
        return self._color_temp

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the color property."""
        return color_util.color_RGB_to_hs(*self._rgb)

    @property
    def brightness(self) -> int:
        """Return the brightness of the device."""
        return self._brightness

    @property
    def available(self) -> bool:
        return self._available

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    async def _update_state(self) -> None:
        try:
            state = await self._device.get_state()
        except (asyncio.TimeoutError, DoHomeException):
            self._available = False
            return
        self._available = True
        if not state["is_on"]:
            self._is_on = False
            return
        self._is_on = True
        if state["mode"] == LightMode.WHITE:
            self._color_mode = ColorMode.COLOR_TEMP
            self._color_temp = state["temperature"]
            self._brightness = state["brightness"]
        elif self._rgb is None:
            self._color_mode = ColorMode.HS
            self._brightness = state["brightness"]
            self._rgb = state["rgb"]
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Reads state from the device"""
        await self._update_state()


    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if ATTR_HS_COLOR in kwargs:
            self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
            self._color_mode = ColorMode.HS
        elif ATTR_COLOR_TEMP_KELVIN in kwargs:
            self._color_temp = kwargs[ATTR_COLOR_TEMP_KELVIN]
            self._color_mode = ColorMode.COLOR_TEMP
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        try:
            if self._color_mode == ColorMode.COLOR_TEMP:
                await self._device.set_white_temperature(
                    self._color_temp,
                    self._brightness)
            else:
                await self._device.set_color(self._rgb, self._brightness)
        except (asyncio.TimeoutError, DoHomeException):
            self._available = False
            return
        self._is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            await self._device.set_power(False)
        except (asyncio.TimeoutError, DoHomeException):
            self._available = False
            return
        self._is_on = False
