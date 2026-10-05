"""Integration tests for Devialet."""

from __future__ import annotations

from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.translation import async_get_translations

from custom_components.devialet.devialet_client.exceptions import (
    DevialetConnectionError,
    DevialetResponseError,
)
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


def _mock_refresh_endpoints(
    mocked,
    *,
    base_url=TEST_BASE_URL,
    device_payload=DEVICE_PAYLOAD,
    system_payload=SYSTEM_PAYLOAD,
) -> None:
    """Register the API endpoints used by the coordinator."""
    mocked.get(f"{base_url}/devices/current", json=device_payload)
    mocked.get(f"{base_url}/systems/current", json=system_payload)
    mocked.get(
        f"{base_url}/groups/current/sources",
        json=SOURCES_PAYLOAD,
    )
    mocked.get(
        f"{base_url}/groups/current/sources/current",
        json=CURRENT_SOURCE_PAYLOAD,
    )
    mocked.get(
        f"{base_url}/groups/current/sources/current/soundControl/volume",
        json=VOLUME_PAYLOAD,
    )
    mocked.get(
        f"{base_url}/systems/current/settings/audio/nightMode",
        json=NIGHT_MODE_PAYLOAD,
    )
    mocked.get(
        f"{base_url}/systems/current/settings/audio/renderingMode",
        json=RENDERING_MODE_PAYLOAD,
    )
    mocked.get(
        f"{base_url}/systems/current/settings/ledMode",
        json=LED_MODE_PAYLOAD,
    )
    mocked.get(
        f"{base_url}/systems/current/settings/powerManagement",
        json=POWER_MANAGEMENT_PAYLOAD,
    )


@pytest.mark.asyncio
async def test_setup_creates_expected_entities(
    hass,
    mock_config_entry,
    aioclient_mock,
) -> None:
    """A config entry should create the expected entities."""
    mock_config_entry.add_to_hass(hass)

    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("media_player.dione").state == "playing"
    assert hass.states.get("switch.dione_night_mode").state == "off"
    assert hass.states.get("switch.dione_auto_power_off").state == "off"
    assert hass.states.get("select.dione_rendering_mode").state == "movie"
    assert hass.states.get("select.dione_led_mode").state == "auto"
    assert hass.states.get("number.dione_auto_power_off_period").state == "90.0"
    assert hass.states.get("button.dione_start_bluetooth_pairing").state == "unknown"
    assert hass.states.get("sensor.dione_auto_power_off_period").state == "90"
    assert hass.states.get("sensor.dione_source_type").attributes["icon"] == (
        "mdi:audio-input-stereo-minijack"
    )
    auto_power_off_period = hass.states.get(
        "sensor.dione_auto_power_off_period"
    )
    assert auto_power_off_period.attributes["device_class"] == "duration"
    assert auto_power_off_period.attributes["state_class"] == "measurement"
    assert auto_power_off_period.attributes["unit_of_measurement"] == "min"
    assert hass.states.get("sensor.dione_codec") is None
    assert hass.states.get("sensor.dione_channels") is None
    assert hass.states.get("binary_sensor.dione_stream_lock") is None

    entity_registry = er.async_get(hass)
    assert (
        entity_registry.async_get("sensor.dione_codec").disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )
    assert (
        entity_registry.async_get("sensor.dione_channels").disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )
    assert (
        entity_registry.async_get("sensor.dione_sampling_rate").disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )
    assert (
        entity_registry.async_get("sensor.dione_bit_depth").disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )
    assert (
        entity_registry.async_get("binary_sensor.dione_stream_lock").disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )
    assert (
        entity_registry.async_get("binary_sensor.dione_lossless").disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )

    media_player_state = hass.states.get("media_player.dione")
    assert media_player_state.attributes["device_available_features"] == [
        "explicitInstallationId",
        "orientation",
        "powerManagement",
        "roomCorrection",
    ]
    assert media_player_state.attributes["system_available_features"] == [
        "ledMode",
        "nightMode",
        "powerManagement",
        "renderingMode",
        "renderingModesPerSourceType",
    ]
    assert media_player_state.attributes["firmware_family"] == "DOS"
    assert media_player_state.attributes["ip_control_version"] == "1"
    assert media_player_state.attributes["device_model"] == "Dione"
    assert media_player_state.attributes["device_model_family"] == "Dione"
    assert media_player_state.attributes["firmware_version"] == "2.18.6"
    assert media_player_state.attributes["stream_codec"] == "pcm"
    assert media_player_state.attributes["stream_channels"] == "5.1.2"
    assert media_player_state.attributes["rendering_mode"] == "movie"


@pytest.mark.parametrize(
    ("device_features", "system_features"),
    [
        (None, None),
        (
            ["powerManagement"],
            ["ledMode", "nightMode", "renderingMode"],
        ),
    ],
)
@pytest.mark.asyncio
async def test_setup_exposes_successfully_probed_optional_features(
    hass,
    mock_config_entry,
    aioclient_mock,
    device_features,
    system_features,
) -> None:
    """Entity setup should follow returned data, not capability metadata alone."""
    device_payload = deepcopy(DEVICE_PAYLOAD)
    system_payload = deepcopy(SYSTEM_PAYLOAD)
    if device_features is None:
        device_payload.pop("availableFeatures")
    else:
        device_payload["availableFeatures"] = device_features
    if system_features is None:
        system_payload.pop("availableFeatures")
    else:
        system_payload["availableFeatures"] = system_features

    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(
        aioclient_mock,
        device_payload=device_payload,
        system_payload=system_payload,
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("switch.dione_night_mode") is not None
    assert hass.states.get("switch.dione_auto_power_off") is not None
    assert hass.states.get("select.dione_rendering_mode") is not None
    assert hass.states.get("select.dione_led_mode") is not None
    assert hass.states.get("number.dione_auto_power_off_period") is not None
    assert hass.states.get("sensor.dione_auto_power_off_period") is not None


@pytest.mark.asyncio
async def test_device_outage_marks_entities_unavailable_and_recovers(
    hass,
    mock_config_entry,
    aioclient_mock,
) -> None:
    """A transient outage should not crash entities and recovery should be automatic."""
    mock_config_entry.add_to_hass(hass)

    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = mock_config_entry.runtime_data
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{TEST_BASE_URL}/devices/current", status=503)
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get("media_player.dione").state == "unavailable"

    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(aioclient_mock)
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get("media_player.dione").state == "playing"


@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["en", "pl", "fr"])
@pytest.mark.parametrize(
    ("failure", "key", "english", "polish"),
    [
        (
            DevialetConnectionError("private connection detail"),
            "device_unavailable",
            "Cannot connect to the Devialet speaker.",
            "Nie można połączyć się z głośnikiem Devialet.",
        ),
        (
            DevialetResponseError("private vendor response", status=500),
            "action_failed",
            "The Devialet speaker could not complete the action.",
            "Głośnik Devialet nie mógł wykonać tej czynności.",
        ),
    ],
)
async def test_device_action_surfaces_home_assistant_error(
    hass,
    mock_config_entry,
    aioclient_mock,
    language,
    failure,
    key,
    english,
    polish,
) -> None:
    """Device connection failures should use Home Assistant's service error surface."""
    hass.config.language = language
    mock_config_entry.add_to_hass(hass)

    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = mock_config_entry.runtime_data
    entity_id = er.async_get(hass).async_get_entity_id(
        "switch", "devialet", f"{coordinator.data.device.serial}_night_mode"
    )
    with patch.object(
        coordinator.client,
        "async_set_night_mode",
        AsyncMock(side_effect=failure),
    ):
        with pytest.raises(HomeAssistantError) as caught:
            await hass.services.async_call(
                SWITCH_DOMAIN,
                SERVICE_TURN_ON,
                {ATTR_ENTITY_ID: entity_id},
                blocking=True,
            )
    error = caught.value
    assert error.translation_domain == "devialet"
    assert error.translation_key == key
    assert error.translation_placeholders is None
    assert error.__cause__ is failure
    assert str(error).startswith(english)
    assert "private" not in str(error)
    translations = await async_get_translations(
        hass, language, "exceptions", {"devialet"}
    )
    assert translations[f"component.devialet.exceptions.{key}.message"].startswith(
        polish if language == "pl" else english
    )
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


@pytest.mark.parametrize("language", ["en", "pl", "fr"])
@pytest.mark.parametrize(
    ("failure", "key", "english", "polish"),
    [
        (
            DevialetConnectionError("private connection detail"),
            "device_unavailable",
            "Cannot connect to the Devialet speaker.",
            "Nie można połączyć się z głośnikiem Devialet.",
        ),
        (
            DevialetResponseError("private vendor payload", status=500),
            "refresh_failed",
            "Could not read the Devialet speaker state.",
            "Nie można odczytać stanu głośnika Devialet.",
        ),
    ],
)
async def test_refresh_failure_retains_translation_and_unavailable_state(
    hass, mock_config_entry, aioclient_mock, language, failure, key, english, polish,
):
    hass.config.language = language
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    coordinator = mock_config_entry.runtime_data
    with patch.object(coordinator.client, "async_refresh", side_effect=failure):
        await coordinator.async_refresh()
        await hass.async_block_till_done()
    error = coordinator.last_exception
    assert isinstance(error, HomeAssistantError)
    assert error.translation_domain == "devialet"
    assert error.translation_key == key
    assert str(error).startswith(english)
    assert "private" not in str(error)
    assert error.__cause__ is failure
    assert not coordinator.last_update_success
    assert hass.states.get("media_player.dione").state == "unavailable"
    translations = await async_get_translations(
        hass, language, "exceptions", {"devialet"}
    )
    assert translations[f"component.devialet.exceptions.{key}.message"].startswith(
        polish if language == "pl" else english
    )
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
