"""Integration tests for Devialet."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from aioresponses import aioresponses
from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
)
from homeassistant.components.media_player import (
    SERVICE_SELECT_SOURCE,
)
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON

from tests.conftest import (
    CURRENT_SOURCE_PAYLOAD,
    DEVICE_PAYLOAD,
    LED_MODE_PAYLOAD,
    NIGHT_MODE_PAYLOAD,
    POWER_MANAGEMENT_PAYLOAD,
    RENDERING_MODE_PAYLOAD,
    SOURCES_PAYLOAD,
    SYSTEM_PAYLOAD,
    TEST_BASE_URL,
    VOLUME_PAYLOAD,
)


def _mock_refresh_endpoints(mocked: aioresponses) -> None:
    """Register the API endpoints used by the coordinator."""
    mocked.get(f"{TEST_BASE_URL}/devices/current", payload=DEVICE_PAYLOAD, repeat=True)
    mocked.get(f"{TEST_BASE_URL}/systems/current", payload=SYSTEM_PAYLOAD, repeat=True)
    mocked.get(
        f"{TEST_BASE_URL}/groups/current/sources", payload=SOURCES_PAYLOAD, repeat=True
    )
    mocked.get(
        f"{TEST_BASE_URL}/groups/current/sources/current",
        payload=CURRENT_SOURCE_PAYLOAD,
        repeat=True,
    )
    mocked.get(
        f"{TEST_BASE_URL}/groups/current/sources/current/soundControl/volume",
        payload=VOLUME_PAYLOAD,
        repeat=True,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/audio/nightMode",
        payload=NIGHT_MODE_PAYLOAD,
        repeat=True,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/audio/renderingMode",
        payload=RENDERING_MODE_PAYLOAD,
        repeat=True,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/ledMode",
        payload=LED_MODE_PAYLOAD,
        repeat=True,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/powerManagement",
        payload=POWER_MANAGEMENT_PAYLOAD,
        repeat=True,
    )


@pytest.mark.asyncio
async def test_setup_creates_expected_entities(hass, mock_config_entry) -> None:
    """A config entry should create the expected entities."""
    mock_config_entry.add_to_hass(hass)

    with aioresponses() as mocked:
        _mock_refresh_endpoints(mocked)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert hass.states.get("media_player.dione").state == "playing"
    assert hass.states.get("switch.dione_night_mode").state == "off"
    assert hass.states.get("select.dione_rendering_mode").state == "movie"
    assert hass.states.get("sensor.dione_codec").state == "pcm"
    assert hass.states.get("sensor.dione_channels").state == "5.1.2"
    assert hass.states.get("binary_sensor.dione_stream_lock").state == "on"
    assert hass.states.get("sensor.dione_auto_power_off_period").state == "90"
    media_player_state = hass.states.get("media_player.dione")
    assert media_player_state.attributes["stream_codec"] == "pcm"
    assert media_player_state.attributes["stream_channels"] == "5.1.2"
    assert media_player_state.attributes["rendering_mode"] == "movie"


@pytest.mark.asyncio
async def test_switch_and_select_use_client_methods(hass, mock_config_entry) -> None:
    """Entity services should delegate to the coordinator client."""
    mock_config_entry.add_to_hass(hass)

    with aioresponses() as mocked:
        _mock_refresh_endpoints(mocked)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    coordinator = mock_config_entry.runtime_data

    with patch.object(
        coordinator.client,
        "async_set_night_mode",
        AsyncMock(),
    ) as set_night_mode:
        with aioresponses() as mocked:
            _mock_refresh_endpoints(mocked)
            await hass.services.async_call(
                SWITCH_DOMAIN,
                SERVICE_TURN_ON,
                {ATTR_ENTITY_ID: "switch.dione_night_mode"},
                blocking=True,
            )
        set_night_mode.assert_awaited_once_with(True)

    with patch.object(
        coordinator.client,
        "async_set_rendering_mode",
        AsyncMock(),
    ) as set_rendering_mode:
        with aioresponses() as mocked:
            _mock_refresh_endpoints(mocked)
            await hass.services.async_call(
                SELECT_DOMAIN,
                SERVICE_SELECT_OPTION,
                {
                    ATTR_ENTITY_ID: "select.dione_rendering_mode",
                    "option": "music",
                },
                blocking=True,
            )
        set_rendering_mode.assert_awaited_once_with("music")

    with patch.object(
        coordinator.client,
        "async_select_source",
        AsyncMock(),
    ) as select_source:
        with aioresponses() as mocked:
            _mock_refresh_endpoints(mocked)
            await hass.services.async_call(
                MEDIA_PLAYER_DOMAIN,
                SERVICE_SELECT_SOURCE,
                {
                    ATTR_ENTITY_ID: "media_player.dione",
                    "source": "Spotify Connect",
                },
                blocking=True,
            )
        select_source.assert_awaited_once_with("2aa14293-aa9e-4ade-ab45-27c89055ea64")
