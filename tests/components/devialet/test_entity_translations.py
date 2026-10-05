"""Translated entity names and existing registry identity contracts."""

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.translation import async_get_translations

from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_SERIAL


@pytest.mark.parametrize(
    ("language", "night_name", "pairing_name"),
    [
        ("en", "Night mode", "Start Bluetooth pairing"),
        ("pl", "Tryb nocny", "Rozpocznij parowanie Bluetooth"),
        ("fr", "Night mode", "Start Bluetooth pairing"),
    ],
)
async def test_names_use_host_translations_and_english_fallback(
    hass, mock_config_entry, aioclient_mock, language, night_name, pairing_name
):
    hass.config.language = language
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    translations = await async_get_translations(hass, language, "entity", {"devialet"})
    registry = er.async_get(hass)
    children = [
        entry
        for entry in er.async_entries_for_config_entry(
            registry, mock_config_entry.entry_id
        )
        if entry.domain != "media_player"
    ]
    assert len(children) == 17
    for child in children:
        assert child.translation_key is not None
        key = f"component.devialet.entity.{child.domain}.{child.translation_key}.name"
        assert child.original_name == translations[key]
        assert child.original_name

    for domain, suffix, expected in (
        ("switch", "night_mode", night_name),
        ("button", "bluetooth_pairing", pairing_name),
    ):
        entity_id = registry.async_get_entity_id(
            domain, "devialet", f"{TEST_SERIAL}_{suffix}"
        )
        assert (
            hass.states.get(entity_id).attributes["friendly_name"]
            == f"Dione {expected}"
        )
    assert hass.states.get("media_player.dione").attributes["friendly_name"] == "Dione"
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_translations_preserve_existing_entity_id_and_user_name(
    hass, mock_config_entry, aioclient_mock
):
    hass.config.language = "pl"
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    old = registry.async_get_or_create(
        "switch",
        "devialet",
        f"{TEST_SERIAL}_night_mode",
        config_entry=mock_config_entry,
        suggested_object_id="dione_night_mode",
        original_name="Night mode",
    )
    registry.async_update_entity(old.entity_id, name="Quiet time")
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    current = registry.async_get(old.entity_id)
    assert current.unique_id == old.unique_id
    assert current.name == "Quiet time"
    assert current.original_name == "Tryb nocny"
    assert hass.states.get(old.entity_id).attributes["friendly_name"] == "Quiet time"
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
