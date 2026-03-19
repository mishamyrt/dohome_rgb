"""Support for DoHome RGB Lights"""

import asyncio
from datetime import timedelta
from typing import Any, Callable, override

import voluptuous as vol
from dohome.api import APIClient
from dohome.exc.base import DoHomeException
from dohome.transport import TCPStream
from dohome.types.constants import KELVIN_MAX, KELVIN_MIN
from dohome.types.device import DeviceInfo as APIDeviceInfo
from dohome.types.device import DeviceType, encode_device_id
from dohome.types.light import LightMode
from homeassistant import config_entries, core
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_RGB_COLOR,
    PLATFORM_SCHEMA,
    LightEntity,
)
from homeassistant.components.light.const import ColorMode
from homeassistant.helpers.device_registry import DeviceInfo

from .constants import CONF_HOST, CONF_INFO, DOMAIN

SCAN_INTERVAL = timedelta(seconds=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_INFO): dict, vol.Required(CONF_HOST): str}
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable[[list[LightEntity]], None],
) -> None:
    """Set up desk light."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    stream = TCPStream(data[CONF_HOST])
    client = APIClient(stream)

    async_add_entities(
        [
            DoHomeLightEntity(
                client,
                data[CONF_INFO],
            )
        ]
    )


class DoHomeLightEntity(LightEntity):
    """DoHome light entity"""

    _attr_supported_color_modes = {ColorMode.RGB, ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = KELVIN_MIN
    _attr_max_color_temp_kelvin = KELVIN_MAX

    _attr_color_mode = ColorMode.COLOR_TEMP

    _client: APIClient
    _info: APIDeviceInfo
    _state_known = False

    def __init__(self, client: APIClient, info: APIDeviceInfo):
        self._client = client
        self._info = info

        hw_info = info["hardware"]
        unique_id = encode_device_id(info["hardware"])
        device_type = DeviceType(hw_info["type"])

        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="DoHome",
            model=device_type.name,
            sw_version=info["version"],
            hw_version=hw_info["chip"],
            serial_number=hw_info["sid"],
        )

    async def _update_state(self) -> None:
        try:
            state = await self._client.get_state()
        except (asyncio.TimeoutError, DoHomeException, OSError):
            self._attr_available = False
            return
        self._attr_available = True
        self._attr_is_on = state["is_on"]
        if not state["is_on"]:
            return

        if not self._state_known:
            if state["mode"] == LightMode.WHITE:
                self._attr_color_mode = ColorMode.COLOR_TEMP
                self._attr_color_temp_kelvin = state["temperature"]
                self._attr_brightness = state["brightness"]
            else:
                self._attr_color_mode = ColorMode.RGB
                self._attr_rgb_color = state["color"]
                self._attr_brightness = state["brightness"]
            self._state_known = True

    async def async_update(self) -> None:
        """Reads state from the device"""
        await self._update_state()
        self.async_write_ha_state()

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        has_explicit_state = (
            ATTR_BRIGHTNESS in kwargs
            or ATTR_RGB_COLOR in kwargs
            or ATTR_COLOR_TEMP_KELVIN in kwargs
        )

        if has_explicit_state:
            self._state_known = True
            if ATTR_BRIGHTNESS in kwargs:
                self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
            if ATTR_RGB_COLOR in kwargs:
                self._attr_color_mode = ColorMode.RGB
                self._attr_rgb_color = kwargs[ATTR_RGB_COLOR]
            elif ATTR_COLOR_TEMP_KELVIN in kwargs:
                self._attr_color_mode = ColorMode.COLOR_TEMP
                self._attr_color_temp_kelvin = kwargs[ATTR_COLOR_TEMP_KELVIN]

        try:
            if not self._state_known:
                await self._client.set_power(True)
            elif self._attr_color_mode == ColorMode.COLOR_TEMP:
                temp = self._attr_color_temp_kelvin or KELVIN_MIN
                brightness = self._attr_brightness or 255
                await self._client.set_white(temp, brightness)
            else:
                color = self._attr_rgb_color or (255, 255, 255)
                brightness = self._attr_brightness or 255
                await self._client.set_color(color, brightness)
        except (asyncio.TimeoutError, DoHomeException, OSError):
            self._attr_available = False
            return
        self._attr_is_on = True

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            await self._client.set_power(False)
            self._attr_is_on = False
        except (asyncio.TimeoutError, DoHomeException, OSError):
            self._attr_available = False
