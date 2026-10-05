"""HA setup remains useful when optional device capabilities are absent."""

from homeassistant.helpers import entity_registry as er

from custom_components.devialet.const import CONF_ENABLE_DEVICE_SETTINGS_SENSORS
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import DEVICE_PAYLOAD, SYSTEM_PAYLOAD, TEST_BASE_URL


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
