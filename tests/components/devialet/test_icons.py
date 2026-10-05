"""HA-loaded icon resources and real entity-state contracts."""

from dataclasses import replace

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.icon import async_get_icons

from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_SERIAL


@pytest.mark.parametrize("enabled", [True, False])
async def test_icons_follow_translation_keys_and_entity_states(
    hass,
    mock_config_entry,
    aioclient_mock,
    enabled,
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    icons = await async_get_icons(hass, "entity", {"devialet"})
    registry = er.async_get(hass)
    coordinator = mock_config_entry.runtime_data
    snapshot = coordinator.data
    coordinator.async_set_updated_data(
        replace(
            snapshot,
            night_mode=replace(
                snapshot.night_mode, night_mode=enabled
            ),
            led_mode=replace(snapshot.led_mode, led_mode="on" if enabled else "off"),
            power_management=replace(
                snapshot.power_management,
                auto_power_off="always" if enabled else "disabled",
            ),
        )
    )
    await hass.async_block_till_done()
    for domain, suffix, key, on_icon, off_icon in (
        (
            "switch",
            "night_mode",
            "night_mode",
            "mdi:weather-night",
            "mdi:weather-sunny",
        ),
        (
            "switch",
            "auto_power_off",
            "auto_power_off",
            "mdi:power-sleep",
            "mdi:power-standby",
        ),
        ("select", "led_mode_select", "led_mode", "mdi:led-on", "mdi:led-off"),
    ):
        entity_id = registry.async_get_entity_id(
            domain, "devialet", f"{TEST_SERIAL}_{suffix}"
        )
        entry = registry.async_get(entity_id)
        state = hass.states.get(entity_id)
        assert entry.translation_key == key
        assert state.state == ("on" if enabled else "off")
        assert "icon" not in state.attributes
        definition = icons["devialet"][domain][key]
        assert definition["state"][state.state] == (
            on_icon if enabled else off_icon
        )
        assert definition["default"]
    assert (
        icons["devialet"]["button"]["bluetooth_pairing"]["default"]
        == "mdi:bluetooth-connect"
    )
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
