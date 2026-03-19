"""DoHome Home Assistant integration"""

import homeassistant.helpers.config_validation as cv
from dohome.types.device import parse_doit_device_info
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .constants import CONF_HOST, CONF_INFO, DOMAIN

CONFIG_SCHEMA = cv.platform_only_config_schema(DOMAIN)  #  pylint: disable=invalid-name
PLATFORMS = [Platform.LIGHT]


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry to new version."""
    if config_entry.version == 1:
        old_data = config_entry.data
        parsed_info = parse_doit_device_info({**old_data[CONF_INFO]})
        _ = hass.config_entries.async_update_entry(
            config_entry,
            data={
                CONF_HOST: old_data[CONF_HOST],
                CONF_INFO: parsed_info,
            },
            version=2,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Generic BT from a config entry."""
    assert entry.unique_id is not None

    host = entry.data[CONF_HOST]
    info = entry.data[CONF_INFO]

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {CONF_HOST: host, CONF_INFO: info}

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _ = await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
