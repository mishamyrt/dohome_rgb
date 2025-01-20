"""DoHome Home Assistant integration config flow."""
from logging import getLogger

import voluptuous as vol
from dohome_api import open_device
from homeassistant import config_entries
from homeassistant.core import callback

from .constants import CONF_HOST, CONF_INFO, DOMAIN

_LOGGER = getLogger(__name__)

class DoHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DoHome bulbs."""

    VERSION = 1

    def __init__(self):
        self.devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the gateway address is entered."""
        errors = {}

        if user_input is not None:
            hostname = user_input.get(CONF_HOST)

            try:
                device = open_device(hostname)
                info = await device.get_info()
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=hostname,
                    data={
                        CONF_HOST: hostname,
                        CONF_INFO: info,
                    },
                )
            except Exception as exc: # pylint: disable=broad-except
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
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the DoHome integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
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
