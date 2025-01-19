"""DoHome Home Assistant integration config flow."""
import voluptuous as vol
from dohome_api import DoHomeGateway
from dohome_api.transport.util import get_discovery_host
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector
from logging import getLogger

from .constants import CONF_GATEWAY, CONF_NAME, CONF_SIDS, DOMAIN

_LOGGER = getLogger(__name__)

def _validate_gateway_address(address: str) -> bool:
    """Basic validation for the gateway address format (IPv4 or multicast format)"""
    try:
        parts = address.split('.')
        if len(parts) != 4 or not all(0 <= int(part) <= 255 for part in parts):
            raise ValueError
        return True
    except ValueError:
        return False

class DoHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DoHome bulbs."""

    VERSION = 1

    def __init__(self):
        self.gateway_address = get_discovery_host()
        self.devices = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the gateway address is entered."""
        errors = {}

        if user_input is not None:
            gateway_address = user_input.get(CONF_GATEWAY)

            if _validate_gateway_address(gateway_address):
                self.gateway_address = gateway_address
                return await self.async_step_device_selection()
            else:
                errors["gateway_address"] = "invalid_gateway"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_GATEWAY, default=self.gateway_address): str
                }
            ),
            errors=errors,
        )

    async def async_step_device_selection(self, user_input=None):
        """Handle the step for device selection and group naming."""
        errors = {}

        gateway = DoHomeGateway(self.gateway_address)
        try:
            self.devices = await gateway.discover_devices(10)
        except Exception as exc: # pylint: disable=broad-except
            _LOGGER.error("Error connecting to gateway: %s", exc)
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            group_name = user_input.get(CONF_NAME)
            selected_devices = user_input.get(CONF_SIDS)

            if group_name and selected_devices:
                return self.async_create_entry(
                    title=group_name,
                    data={
                        CONF_GATEWAY: self.gateway_address,
                        CONF_NAME: group_name,
                        CONF_SIDS: selected_devices,
                    },
                )
            else:
                errors["base"] = "incomplete_data"

        return self.async_show_form(
            step_id="device_selection",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="DoHome Light"): str,
                    vol.Required(CONF_SIDS): selector({
                        "multiple": True,
                        "select": {
                            "options": {device: device for device in self.devices},
                        }
                    })
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
                        CONF_GATEWAY,
                        default=self.config_entry.data.get(CONF_GATEWAY, "255.255.255.255"),
                    ): str,
                    vol.Optional(
                        CONF_NAME,
                        default=self.config_entry.data.get(CONF_NAME, "DoHome Light"),
                    ): str,
                }
            ),
        )
