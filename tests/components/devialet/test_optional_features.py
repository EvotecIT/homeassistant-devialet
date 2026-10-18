"""HA setup remains useful when optional device capabilities are absent."""

import pytest
from homeassistant.helpers import entity_registry as er

from custom_components.devialet.const import CONF_ENABLE_DEVICE_SETTINGS_SENSORS
from custom_components.devialet.devialet_client.const import (
    POWER_MANAGEMENT_AUDIO_ENDPOINT,
)
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import (
    CURRENT_SOURCE_PAYLOAD,
    DEVICE_PAYLOAD,
    SYSTEM_PAYLOAD,
    TEST_BASE_URL,
)


async def test_basic_device_without_optional_endpoints_loads_without_controls(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.get(
        f"{TEST_BASE_URL}/devices/current",
        json={**DEVICE_PAYLOAD, "availableFeatures": []},
    )
    aioclient_mock.get(
        f"{TEST_BASE_URL}/systems/current",
        json={**SYSTEM_PAYLOAD, "availableFeatures": []},
    )
    aioclient_mock.get(f"{TEST_BASE_URL}/groups/current/sources", json={"sources": []})
    for endpoint in (
        "/groups/current/sources/current",
        "/groups/current/sources/current/soundControl/volume",
        "/systems/current/sources/current/soundControl/volume",
    ):
        aioclient_mock.get(f"{TEST_BASE_URL}{endpoint}", status=404)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    try:
        state = hass.states.get("media_player.dione")
        assert state.state == "idle"
        assert not state.attributes.get("source_list")
        assert state.attributes.get("volume_level") is None
        registry = er.async_get(hass)
        entries = er.async_entries_for_config_entry(
            registry, mock_config_entry.entry_id
        )
        assert not any(
            entry.domain in {"switch", "select", "number", "button"}
            for entry in entries
        )
        assert not any(
            "/settings/" in str(call[1]) for call in aioclient_mock.mock_calls
        )
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_optional_settings_disappear_and_recover_without_stale_values(
    hass, mock_config_entry, aioclient_mock
):
    """Existing entities reflect missing settings without losing their IDs."""
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    expected = {
        "select.dione_rendering_mode": "movie",
        "select.dione_led_mode": "auto",
        "number.dione_auto_power_off_period": "90.0",
        "switch.dione_night_mode": "off",
        "switch.dione_auto_power_off": "off",
    }
    registry = er.async_get(hass)
    identities = {
        entity_id: registry.async_get(entity_id).unique_id for entity_id in expected
    }
    coordinator = mock_config_entry.runtime_data
    try:
        aioclient_mock.clear_requests()
        _mock_refresh_endpoints(aioclient_mock, optional_status=404)
        aioclient_mock.get(
            f"{TEST_BASE_URL}{POWER_MANAGEMENT_AUDIO_ENDPOINT}", status=404
        )
        await coordinator.async_refresh()
        await hass.async_block_till_done()

        assert coordinator.last_update_success
        assert hass.states.get("media_player.dione").state == "playing"
        for entity_id in expected:
            assert hass.states.get(entity_id).state == "unknown"
        rendering = hass.states.get("select.dione_rendering_mode")
        assert rendering.attributes["options"] == []

        aioclient_mock.clear_requests()
        _mock_refresh_endpoints(aioclient_mock)
        await coordinator.async_refresh()
        await hass.async_block_till_done()

        for entity_id, state in expected.items():
            assert hass.states.get(entity_id).state == state
            assert registry.async_get(entity_id).unique_id == identities[entity_id]
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_device_setting_sensor_opt_out_preserves_controls(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_ENABLE_DEVICE_SETTINGS_SENSORS: False}
    )
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    try:
        registry = er.async_get(hass)
        for name in (
            "led_mode",
            "led_control",
            "auto_power_off_mode",
            "auto_power_off_period",
        ):
            assert registry.async_get(f"sensor.dione_{name}") is None
        assert hass.states.get("sensor.dione_source_type") is not None
        assert hass.states.get("select.dione_led_mode") is not None
        assert hass.states.get("number.dione_auto_power_off_period") is not None
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


@pytest.mark.parametrize(
    ("playing_state", "title", "unlisted_source", "expected_state", "expected_source"),
    [("paused", "Fixture Track", False, "paused", "HDMI"),
     ("stopped", "", True, "on", "Optical")],
)
async def test_media_state_and_metadata_use_current_source_payload(
    hass, mock_config_entry, aioclient_mock, playing_state, title,
    unlisted_source, expected_state, expected_source,
):
    """Playback state and title remain useful while a source list is catching up."""
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    payload = {
        **CURRENT_SOURCE_PAYLOAD,
        "playingState": playing_state,
        "metadata": {**CURRENT_SOURCE_PAYLOAD["metadata"], "title": title},
    }
    if unlisted_source:
        payload["source"] = {
            **payload["source"], "type": "optical",
            "sourceId": "00000000-0000-4000-8000-000000000999",
        }
    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(aioclient_mock, source_state_payload=payload)
    try:
        await mock_config_entry.runtime_data.async_refresh()
        await hass.async_block_till_done()
        state = hass.states.get("media_player.dione")
        assert state.state == expected_state
        assert state.attributes["source"] == expected_source
        assert state.attributes["media_title"] == (title or expected_source)
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
