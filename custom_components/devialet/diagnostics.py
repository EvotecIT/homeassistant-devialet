"""Diagnostics support for Devialet."""

from __future__ import annotations

from dataclasses import asdict

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import CONF_PATH

TO_REDACT = {
    CONF_HOST,
    CONF_PORT,
    CONF_PATH,
    "device_id",
    "group_id",
    "system_id",
    "installation_id",
    "serial",
    "source_id",
}


async def async_get_config_entry_diagnostics(hass, entry) -> dict[str, object]:
    """Return diagnostics for a config entry."""
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "snapshot": async_redact_data(asdict(entry.runtime_data.data), TO_REDACT),
    }
