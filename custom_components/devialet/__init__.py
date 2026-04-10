"""The Devialet integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from .coordinator import DevialetConfigEntry, DevialetCoordinator

PLATFORMS = [
    Platform.MEDIA_PLAYER,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass, entry: DevialetConfigEntry) -> bool:
    """Set up Devialet from a config entry."""
    coordinator = DevialetCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await _async_migrate_media_player_entity(hass, entry, coordinator)
    await _async_cleanup_stale_entities(hass, entry, coordinator)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry: DevialetConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass, entry: DevialetConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_migrate_media_player_entity(
    hass,
    entry: DevialetConfigEntry,
    coordinator: DevialetCoordinator,
) -> None:
    """Remove the old custom media-player duplicate if it exists."""
    entity_registry = er.async_get(hass)
    serial = coordinator.data.device.serial
    if serial is None:
        return

    legacy_unique_id = f"{serial}_media_player"
    current_unique_id = serial

    current_exists = False
    legacy_entity_id: str | None = None

    for registry_entry in er.async_entries_for_config_entry(
        entity_registry,
        entry.entry_id,
    ):
        if registry_entry.domain != Platform.MEDIA_PLAYER:
            continue
        if registry_entry.unique_id == current_unique_id:
            current_exists = True
        if registry_entry.unique_id == legacy_unique_id:
            legacy_entity_id = registry_entry.entity_id

    if legacy_entity_id is None:
        return

    if current_exists:
        entity_registry.async_remove(legacy_entity_id)
        return

    entity_registry.async_update_entity(
        legacy_entity_id,
        new_unique_id=current_unique_id,
    )


async def _async_cleanup_stale_entities(
    hass,
    entry: DevialetConfigEntry,
    coordinator: DevialetCoordinator,
) -> None:
    """Remove stale entities from older custom-integration revisions."""
    entity_registry = er.async_get(hass)
    serial = coordinator.data.device.serial
    if serial is None:
        return

    stale_unique_ids = {
        f"{serial}_auto_power_off",
    }

    for registry_entry in er.async_entries_for_config_entry(
        entity_registry,
        entry.entry_id,
    ):
        if registry_entry.unique_id in stale_unique_ids:
            entity_registry.async_remove(registry_entry.entity_id)
