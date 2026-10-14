"""Idle speakers remain reachable even when no source is selected."""

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType

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
    TEST_HOST,
    TEST_PORT,
    VOLUME_PAYLOAD,
)

NO_CURRENT_SOURCE = {"error": {"code": "NoCurrentSource"}}


def mock_speaker(mocked, *, idle=True, volume_error=None):
    """Expose the normal device endpoints with source-dependent responses."""
    mocked.clear_requests()
    responses = {
        "/devices/current": DEVICE_PAYLOAD,
        "/systems/current": SYSTEM_PAYLOAD,
        "/groups/current/sources": SOURCES_PAYLOAD,
        "/groups/current/sources/current": (
            NO_CURRENT_SOURCE if idle else CURRENT_SOURCE_PAYLOAD
        ),
        "/groups/current/sources/current/soundControl/volume": (
            volume_error or (NO_CURRENT_SOURCE if idle else VOLUME_PAYLOAD)
        ),
        "/systems/current/sources/current/soundControl/volume": (
            volume_error or (NO_CURRENT_SOURCE if idle else VOLUME_PAYLOAD)
        ),
        "/systems/current/settings/audio/nightMode": NIGHT_MODE_PAYLOAD,
        "/systems/current/settings/audio/renderingMode": RENDERING_MODE_PAYLOAD,
        "/systems/current/settings/ledMode": LED_MODE_PAYLOAD,
        "/systems/current/settings/powerManagement": POWER_MANAGEMENT_PAYLOAD,
    }
    for endpoint, payload in responses.items():
        mocked.get(f"{TEST_BASE_URL}{endpoint}", json=payload)


async def test_idle_user_flow(hass, aioclient_mock):
    """A reachable idle speaker passes the same validation used by manual setup."""
    mock_speaker(aioclient_mock)
    result = await hass.config_entries.flow.async_init(
        "devialet",
        context={"source": config_entries.SOURCE_USER},
        data={CONF_HOST: TEST_HOST, CONF_PORT: TEST_PORT},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_idle_setup_and_playback_transitions(
    hass, mock_config_entry, aioclient_mock
):
    """Idle setup and subsequent source changes keep system controls available."""
    mock_speaker(aioclient_mock)
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    for idle, volume_absent in (
        (True, True), (False, False), (False, True), (True, True)
    ):
        mock_speaker(
            aioclient_mock,
            idle=idle,
            volume_error=NO_CURRENT_SOURCE if volume_absent else None,
        )
        await mock_config_entry.runtime_data.async_refresh()
        await hass.async_block_till_done()
        player = hass.states.get("media_player.dione")
        assert player.state == ("idle" if idle else "playing")
        assert player.attributes.get("volume_level") == (
            None if volume_absent else 0.47
        )
        assert player.attributes.get("source") == (None if idle else "HDMI")
        assert hass.states.get("switch.dione_night_mode").state == "off"
        assert hass.states.get("switch.dione_auto_power_off").state == "off"
        assert hass.states.get("number.dione_auto_power_off_period").state == "90.0"
        assert (
            hass.states.get("button.dione_start_bluetooth_pairing").state == "unknown"
        )

    aioclient_mock.post(
        f"{TEST_BASE_URL}/systems/current/settings/audio/nightMode", json={}
    )
    aioclient_mock.post(
        f"{TEST_BASE_URL}/systems/current/bluetooth/startAdvertising", json={}
    )
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": "switch.dione_night_mode"}, blocking=True
    )
    await hass.services.async_call(
        "button", "press",
        {"entity_id": "button.dione_start_bluetooth_pairing"}, blocking=True,
    )
    assert hass.states.get("media_player.dione").state == "idle"

    # A different API error still makes the coordinator unavailable; recovery
    # does not require playback to start.
    mock_speaker(aioclient_mock, volume_error={"error": {"code": "InternalError"}})
    await mock_config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get("media_player.dione").state == "unavailable"
    mock_speaker(aioclient_mock)
    await mock_config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get("media_player.dione").state == "idle"
