"""Diagnostics support for Devialet."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .const import CONF_PATH
from .coordinator import DevialetConfigEntry

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
    "unique_id",
    "title",
    "device_name",
    "system_name",
    "peer_device_name",
    "artist",
    "album",
    "cover_art_url",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: DevialetConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    snapshot = asdict(entry.runtime_data.data)
    # HA redaction traverses lists and dicts; dataclasses preserve source tuples.
    snapshot["sources"] = list(snapshot["sources"])
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "snapshot": async_redact_data(snapshot, TO_REDACT),
    }
