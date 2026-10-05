"""HA actions reach the documented client wire contract without device access."""

from dataclasses import replace

import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.devialet.const import DEFAULT_PATH
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_BASE_URL, TEST_HOST, TEST_PORT

PLAYBACK = "/groups/current/sources/current/playback"
SOUND = "/groups/current/sources/current/soundControl"
SETTINGS = "/systems/current/settings"


@pytest.mark.parametrize(
    ("domain", "action", "entity", "arguments", "endpoint", "payload"),
    [
        ("media_player", "media_play", "dione", {}, f"{PLAYBACK}/play", {}),
        ("media_player", "media_pause", "dione", {}, f"{PLAYBACK}/pause", {}),
        ("media_player", "media_stop", "dione", {}, f"{PLAYBACK}/pause", {}),
        ("media_player", "media_next_track", "dione", {}, f"{PLAYBACK}/next", {}),
        (
            "media_player",
            "media_previous_track",
            "dione",
            {},
            f"{PLAYBACK}/previous",
            {},
        ),
        (
            "media_player",
            "media_seek",
            "dione",
            {"seek_position": 25.9},
            f"{PLAYBACK}/position",
            {"position": 25},
        ),
        (
            "media_player",
            "volume_set",
            "dione",
            {"volume_level": 0.42},
            f"{SOUND}/volume",
            {"volume": 42},
        ),
        ("media_player", "volume_up", "dione", {}, f"{SOUND}/volumeUp", {}),
        ("media_player", "volume_down", "dione", {}, f"{SOUND}/volumeDown", {}),
        (
            "media_player",
            "volume_mute",
            "dione",
            {"is_volume_muted": True},
            f"{PLAYBACK}/mute",
            {},
        ),
        (
            "media_player",
            "volume_mute",
            "dione",
            {"is_volume_muted": False},
            f"{PLAYBACK}/unmute",
            {},
        ),
        (
            "media_player",
            "select_source",
            "dione",
            {"source": "Spotify-Connect"},
            "/groups/current/sources/00000000-0000-4000-8000-000000000105/playback/play",
            {},
        ),
        ("media_player", "turn_off", "dione", {}, "/systems/current/powerOff", {}),
        (
            "switch",
            "turn_on",
            "dione_night_mode",
            {},
            f"{SETTINGS}/audio/nightMode",
            {"nightMode": "on"},
        ),
        (
            "switch",
            "turn_off",
            "dione_night_mode",
            {},
            f"{SETTINGS}/audio/nightMode",
            {"nightMode": "off"},
        ),
        (
            "switch",
            "turn_on",
            "dione_auto_power_off",
            {},
            f"{SETTINGS}/powerManagement",
            {"autoPowerOff": "always", "autoPowerOffPeriod": 90},
        ),
        (
            "switch",
            "turn_off",
            "dione_auto_power_off",
            {},
            f"{SETTINGS}/powerManagement",
            {"autoPowerOff": "disabled", "autoPowerOffPeriod": 90},
        ),
        (
            "select",
            "select_option",
            "dione_rendering_mode",
            {"option": "music"},
            f"{SETTINGS}/audio/renderingMode",
            {"renderingMode": "music"},
        ),
        (
            "select",
            "select_option",
            "dione_led_mode",
            {"option": "off"},
            f"{SETTINGS}/ledMode",
            {"ledMode": "off", "ledControl": "manual"},
        ),
        (
            "number",
            "set_value",
            "dione_auto_power_off_period",
            {"value": 120},
            f"{SETTINGS}/powerManagement",
            {"autoPowerOffPeriod": 120},
        ),
        (
            "button",
            "press",
            "dione_start_bluetooth_pairing",
            {},
            "/systems/current/bluetooth/startAdvertising",
            {},
        ),
    ],
)
async def test_ha_action_sends_expected_request(
    hass,
    mock_config_entry,
    aioclient_mock,
    domain,
    action,
    entity,
    arguments,
    endpoint,
    payload,
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    aioclient_mock.post(f"{TEST_BASE_URL}{endpoint}", json={})
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    coordinator = mock_config_entry.runtime_data
    coordinator.async_set_updated_data(
        replace(
            coordinator.data,
            source_state=replace(
                coordinator.data.source_state,
                available_operations=("play", "pause", "next", "previous", "seek"),
            ),
        )
    )
    await hass.async_block_till_done()
    try:
        if action == "select_source":
            assert (
                "Spotify Connect"
                in hass.states.get("media_player.dione").attributes["source_list"]
            )
        await hass.services.async_call(
            domain,
            action,
            {"entity_id": f"{domain}.{entity}", **arguments},
            blocking=True,
        )
        writes = [call for call in aioclient_mock.mock_calls if call[0] == "POST"]
        assert len(writes) == 1
        assert writes[0][1].host == TEST_HOST
        assert writes[0][1].port == TEST_PORT
        assert writes[0][1].path == f"{DEFAULT_PATH}{endpoint}"
        assert writes[0][2] == payload
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


@pytest.mark.parametrize("index", [0, 1])
async def test_same_type_sources_with_shared_prefix_remain_selectable(
    hass, mock_config_entry, aioclient_mock, index
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    coordinator = mock_config_entry.runtime_data
    source = coordinator.data.sources[3]
    sources = (
        source,
        replace(source, source_id="00000000-0000-4000-8000-000000000199"),
    )
    coordinator.async_set_updated_data(replace(coordinator.data, sources=sources))
    await hass.async_block_till_done()
    options = hass.states.get("media_player.dione").attributes["source_list"]
    assert options == [f"HDMI ({item.source_id})" for item in sources]
    endpoint = f"/groups/current/sources/{sources[index].source_id}/playback/play"
    aioclient_mock.post(f"{TEST_BASE_URL}{endpoint}", json={})
    try:
        await hass.services.async_call(
            "media_player",
            "select_source",
            {"entity_id": "media_player.dione", "source": options[index]},
            blocking=True,
        )
        writes = [call for call in aioclient_mock.mock_calls if call[0] == "POST"]
        assert len(writes) == 1
        assert writes[0][1].path == f"{DEFAULT_PATH}{endpoint}"
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_unknown_source_is_a_user_action_error_without_network_write(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    try:
        with pytest.raises(ServiceValidationError, match="Unknown Devialet source"):
            await hass.services.async_call(
                "media_player",
                "select_source",
                {"entity_id": "media_player.dione", "source": "Missing source"},
                blocking=True,
            )
        assert not any(call[0] == "POST" for call in aioclient_mock.mock_calls)
    finally:
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
