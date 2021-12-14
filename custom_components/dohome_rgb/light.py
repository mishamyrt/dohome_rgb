"""Support for DoHome RGB Lights"""
from __future__ import annotations
from typing import Any, Final
import logging
from datetime import timedelta
import homeassistant.util.color as color_util
import homeassistant.helpers.config_validation as cv
import homeassistant.components.light as light
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    COLOR_MODE_COLOR_TEMP,
    COLOR_MODE_HS,
    LightEntity,
)

from .convert import _dohome_percent, _dohome_to_uint8, _uint8_to_dohome
from .dohome_api import _send_command, _get_device_info

_LOGGER = logging.getLogger(__name__)

CONF_ENTITIES: Final = "entities"

SCAN_INTERVAL = timedelta(seconds=6)
PLATFORM_SCHEMA: Final = light.PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENTITIES, default={}): {cv.string: cv.string},
})


# pylint: disable=unused-argument
def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> bool:
    """Initialise submitted devices."""
    devices = []
    for name, address in config[CONF_ENTITIES].items():
        _LOGGER.info("Added device %s", name)
        devices.append(DoHomeLight(name, address))
    if len(devices) > 0:
        add_devices(devices)


class DoHomeLight(LightEntity):
    """Entity of the DoHome light device."""

    _sid: str | None = None
    _state: bool = False
    _available: bool = False
    _rgb: tuple[int, int, int] = (255, 255, 255)
    _brightness: int = 255
    _color_temp: int = 255
    _color_mode = COLOR_MODE_HS

    def __init__(self, name: str, address: str):
        self._name: Final = name
        self._address: Final = address

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique id of the device."""
        return self._name

    @property
    def brightness(self) -> int:
        """Return the brightness of the device."""
        return self._brightness

    @property
    def color_mode(self):
        """Return the color mode of the device."""
        return self._color_mode

    @property
    def available(self) -> bool:
        """Return status of the device."""
        return self._available

    @property
    def hs_color(self) -> tuple[int, int, int]:
        """Return the color of the device."""
        return color_util.color_RGB_to_hs(*self._rgb)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._state

    @property
    def color_temp(self) -> int:
        """Return the CT color value in mireds."""
        return self._color_temp

    @property
    def supported_color_modes(self) -> int:
        """Flag supported color modes."""
        return {COLOR_MODE_HS, COLOR_MODE_COLOR_TEMP}

    @property
    def min_mireds(self) -> int:
        """Return the coldest color_temp that this light supports."""
        return 0

    @property
    def max_mireds(self) -> int:
        """Return the warmest color_temp that this light supports."""
        return 255

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        color = (0, 0, 0)
        white = (0, 0)

        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        if ATTR_HS_COLOR in kwargs:
            self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
            self._color_mode = COLOR_MODE_HS
        elif ATTR_COLOR_TEMP in kwargs:
            self._color_temp = kwargs[ATTR_COLOR_TEMP]
            self._color_mode = COLOR_MODE_COLOR_TEMP

        brightness = self._brightness / 255

        def apply_brigthness(values: list[int]):
            return tuple(map(lambda i: i * brightness, values))

        if self._color_mode is COLOR_MODE_HS:
            color = map(_uint8_to_dohome, list(self._rgb))
        elif self._color_mode is COLOR_MODE_COLOR_TEMP:
            warm = _uint8_to_dohome(self._color_temp)
            white = [5000 - warm, warm]

        self._set_state(
            apply_brigthness(color),
            apply_brigthness(white)
        )
        self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        self._set_state((0, 0, 0), (0, 0))
        self._state = False

    def _set_state(
        self,
        rgb: tuple[float, float, float],
        white: tuple[float, float]
    ) -> None:
        """Set state to the device."""
        data = {
            "r": int(rgb[0]),
            "g": int(rgb[1]),
            "b": int(rgb[2]),
            "w": int(white[0]),
            "m": int(white[1])
        }
        _LOGGER.debug("update %s: %s", self._address, data)
        self._send_command(6, data)

    def update(self, is_first: bool = False) -> None:
        """Load state from the device."""
        if self._sid is None:
            info = _get_device_info(self._address)
            if info is None:
                return
            self._sid = info["device_name"][-4:]
            return self.update(True)

        state = self._send_command(25)
        _LOGGER.debug("got state: %s", state)
        if state is None:
            return
        if state["r"] + state["g"] + state["b"] == 0:
            if state["w"] + state["m"] == 0:
                self._state = False
            else:
                brighness_percent = _dohome_percent(state["m"] + state["w"])
                self._state = True
                self._color_mode = COLOR_MODE_COLOR_TEMP
                self._brightness = 255 * brighness_percent
                self._color_temp = _dohome_to_uint8(state["m"] / brighness_percent)
        else:
            self._state = True
            self._color_mode = COLOR_MODE_HS
            if not is_first:
                return
            self._rgb = tuple(map(_dohome_to_uint8, (state["r"], state["g"], state["b"])))
            self._brightness = 255

    def _send_command(self, cmd: str, data: Any = None) -> dict | None:
        """Send command to the device."""
        result = _send_command(
            self._address,
            self._sid,
            cmd,
            data
        )
        self._available = result is not None
        return result
