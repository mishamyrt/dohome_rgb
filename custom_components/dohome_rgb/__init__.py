"""DoHome Home Assistant integration"""
import homeassistant.helpers.config_validation as cv
from dohome_api import DoHomeGateway
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .constants import CONF_GATEWAY, CONF_NAME, CONF_SIDS, DOMAIN

CONFIG_SCHEMA = cv.platform_only_config_schema(DOMAIN)
PLATFORMS = [Platform.LIGHT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Generic BT from a config entry."""
    assert entry.unique_id is not None
    hass.data.setdefault(DOMAIN, {})

    device_id = "_".join(entry.data[CONF_SIDS])

    hass.data[DOMAIN][entry.entry_id] = {
        "sids": entry.data[CONF_SIDS],
        "gateway": entry.data[CONF_GATEWAY],
        "info": {
            "identifiers": {
                (DOMAIN, device_id)
            },
            "name": f"DoHome {entry.data[CONF_NAME]}",
            "manufacturer": "DoHome",
            "model": "WiFi RGB light bulb",
        },
        "id": device_id
    }

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
