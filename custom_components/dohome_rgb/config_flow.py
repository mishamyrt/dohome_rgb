"""DoHome Home Assistant integration config flow."""

from __future__ import annotations

from logging import getLogger
from typing import override

import voluptuous as vol
from dohome.api import APIClient
from dohome.transport import TCPStream
from dohome.types.device import encode_device_id
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback

from .constants import CONF_HOST, CONF_INFO, DOMAIN

_LOGGER = getLogger(__name__)


class DoHomeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DoHome bulbs."""

    VERSION: int = 2

    def __init__(self):
        pass

    @override
    async def async_step_user(self, user_input: dict[str, str] | None = None):
        """Handle the initial step where the gateway address is entered."""
        errors: dict[str, str] = {}

        if user_input is not None:
            hostname = user_input.get(CONF_HOST)
            if hostname is None:
                # This branch should be unreachable due to the form validation
                raise ValueError("Missing host")
            try:
                stream = TCPStream(hostname)
                client = APIClient(stream)
                info = await client.get_device_info()
                unique_id = encode_device_id(info["hardware"])

                _ = await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=hostname,
                    data={
                        CONF_HOST: hostname,
                        CONF_INFO: info,
                    },
                )
            except Exception as exc:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.exception("Error connecting to device: %s", exc)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @override
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return OptionsFlowHandler()


class OptionsFlowHandler(OptionsFlow):
    """Handle options flow for the DoHome integration."""

    async def async_step_init(self, user_input: dict[str, str] | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_HOST,
                        default=self.config_entry.data.get(CONF_HOST, ""),
                    ): str,
                }
            ),
        )
