"""The Devialet integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN
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


async def async_setup_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> bool:
    """Set up Devialet from a config entry."""
    # Subscribe before network awaits so a new connection cannot be lost.
    reload_settings = (entry.data, entry.options, entry.title, entry.unique_id)

    async def async_reload_changed_settings(
        hass: HomeAssistant, updated_entry: DevialetConfigEntry,
    ) -> None:
        nonlocal reload_settings
        settings = (
            updated_entry.data, updated_entry.options,
            updated_entry.title, updated_entry.unique_id,
        )
        if settings == reload_settings:
            return
        reload_settings = settings
        await async_reload_entry(hass, updated_entry)

    entry.async_on_unload(entry.add_update_listener(async_reload_changed_settings))
    coordinator = DevialetCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await _async_migrate_media_player_entity(hass, entry, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> None:
    """Remove the identity repair when its entry is deleted."""
    ir.async_delete_issue(hass, DOMAIN, f"device_identity_{entry.entry_id}")


async def _async_migrate_media_player_entity(
    hass: HomeAssistant,
    entry: DevialetConfigEntry,
    coordinator: DevialetCoordinator,
) -> None:
    """Restore the registry identity and migrate the old media-player ID."""
    entity_registry = er.async_get(hass)
    serial = coordinator.data.device.serial
    media_entries = {
        row.unique_id: row.entity_id
        for row in er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        if row.domain == Platform.MEDIA_PLAYER
    }
    existing_identity = next(
        (identity for identity in (serial, entry.entry_id)
         if identity in media_entries),
        None,
    )
    if existing_identity is None:
        existing_identity = next(
            (identity for identity in media_entries
             if not identity.endswith("_media_player")),
            None,
        )
    legacy_unique_id = f"{serial}_media_player"
    if existing_identity is not None:
        coordinator.registry_identity = existing_identity
    elif serial is not None and (
        legacy_unique_id in media_entries
        or entry.unique_id != coordinator.data.device.device_id
    ):
        coordinator.registry_identity = serial
    # New UUID-based entries keep their entry ID if a serial appears later.
    # Existing serial-based rows retain their namespace even without a serial.
    if serial is None or coordinator.registry_identity != serial:
        return

    current_unique_id = serial
    legacy_entity_id = media_entries.get(legacy_unique_id)
    if legacy_entity_id is None:
        return

    if current_unique_id in media_entries:
        entity_registry.async_remove(legacy_entity_id)
        return

    entity_registry.async_update_entity(
        legacy_entity_id,
        new_unique_id=current_unique_id,
    )
