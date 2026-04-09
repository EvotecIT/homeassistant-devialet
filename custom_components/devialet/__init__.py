"""The Devialet integration."""

from __future__ import annotations

from homeassistant.const import Platform

from .coordinator import DevialetConfigEntry, DevialetCoordinator

PLATFORMS = [
    Platform.MEDIA_PLAYER,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass, entry: DevialetConfigEntry) -> bool:
    """Set up Devialet from a config entry."""
    coordinator = DevialetCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry: DevialetConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
