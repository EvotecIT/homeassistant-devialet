"""Legacy media-player migration preserves the surviving registry identity."""

import pytest
from homeassistant.helpers import entity_registry as er

from custom_components.devialet.const import DOMAIN
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import DEVICE_PAYLOAD, TEST_DEVICE_ID, TEST_SERIAL


@pytest.mark.parametrize("scenario", ["legacy_only", "duplicate", "no_serial"])
async def test_legacy_media_player_registry_migration(
    hass, mock_config_entry, aioclient_mock, scenario
):
    """Migrate the old unique ID without discarding user customization."""
    mock_config_entry.add_to_hass(hass)
    if scenario == "no_serial":
        # A setup flow without a serial saves the device ID as its identity.
        hass.config_entries.async_update_entry(
            mock_config_entry, unique_id=TEST_DEVICE_ID,
        )
    registry = er.async_get(hass)
    legacy = registry.async_get_or_create(
        "media_player", DOMAIN, f"{TEST_SERIAL}_media_player",
        config_entry=mock_config_entry, suggested_object_id="living_room_audio",
    )
    legacy = registry.async_update_entity(
        legacy.entity_id, name="Living Room Audio", icon="mdi:music",
        disabled_by=er.RegistryEntryDisabler.USER,
    )
    unrelated = registry.async_get_or_create(
        "sensor", DOMAIN, "retained_sensor", config_entry=mock_config_entry,
    )
    current = None
    if scenario == "duplicate":
        current = registry.async_get_or_create(
            "media_player", DOMAIN, TEST_SERIAL,
            config_entry=mock_config_entry, suggested_object_id="current_audio",
        )
        current = registry.async_update_entity(
            current.entity_id, name="Current Audio",
            disabled_by=er.RegistryEntryDisabler.USER,
        )
    _mock_refresh_endpoints(
        aioclient_mock,
        device_payload={**DEVICE_PAYLOAD, "serial": None}
        if scenario == "no_serial" else DEVICE_PAYLOAD,
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    try:
        if scenario == "duplicate":
            assert registry.async_get(legacy.entity_id) is None
            surviving = registry.async_get(current.entity_id)
            assert surviving.unique_id == TEST_SERIAL
            assert surviving.name == "Current Audio"
            assert surviving.disabled_by is er.RegistryEntryDisabler.USER
        else:
            surviving = registry.async_get(legacy.entity_id)
            assert surviving.unique_id == (
                legacy.unique_id if scenario == "no_serial" else TEST_SERIAL
            )
            assert surviving.entity_id == legacy.entity_id
            assert surviving.name == "Living Room Audio"
            assert surviving.icon == "mdi:music"
            assert surviving.disabled_by is er.RegistryEntryDisabler.USER
        assert registry.async_get(unrelated.entity_id).unique_id == unrelated.unique_id
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
