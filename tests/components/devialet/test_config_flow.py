"""Config-flow tests for Devialet."""

from __future__ import annotations

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.devialet.const import (
    CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
    CONF_PATH,
    CONF_SCAN_INTERVAL,
    DEFAULT_PATH,
    DOMAIN,
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
    TEST_HOST,
    TEST_PORT,
    VOLUME_PAYLOAD,
)


def _mock_refresh_endpoints(mocked) -> None:
    """Register the API endpoints used during validation and refresh."""
    mocked.get(f"{TEST_BASE_URL}/devices/current", json=DEVICE_PAYLOAD)
    mocked.get(f"{TEST_BASE_URL}/systems/current", json=SYSTEM_PAYLOAD)
    mocked.get(
        f"{TEST_BASE_URL}/groups/current/sources",
        json=SOURCES_PAYLOAD,
    )
    mocked.get(
        f"{TEST_BASE_URL}/groups/current/sources/current",
        json=CURRENT_SOURCE_PAYLOAD,
    )
    mocked.get(
        f"{TEST_BASE_URL}/groups/current/sources/current/soundControl/volume",
        json=VOLUME_PAYLOAD,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/audio/nightMode",
        json=NIGHT_MODE_PAYLOAD,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/audio/renderingMode",
        json=RENDERING_MODE_PAYLOAD,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/ledMode",
        json=LED_MODE_PAYLOAD,
    )
    mocked.get(
        f"{TEST_BASE_URL}/systems/current/settings/powerManagement",
        json=POWER_MANAGEMENT_PAYLOAD,
    )


@pytest.mark.asyncio
async def test_user_flow_creates_entry(hass, aioclient_mock) -> None:
    """Manual setup should validate the speaker and create an entry."""
    _mock_refresh_endpoints(aioclient_mock)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data={CONF_HOST: TEST_HOST, CONF_PORT: TEST_PORT},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Dione"
    assert result["data"] == {
        CONF_HOST: TEST_HOST,
        CONF_PORT: TEST_PORT,
        CONF_PATH: DEFAULT_PATH,
    }


@pytest.mark.asyncio
async def test_options_flow_saves_settings(hass) -> None:
    """Options should open and persist through Home Assistant's flow manager."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DEVICE_PAYLOAD["serial"],
        data={
            CONF_HOST: TEST_HOST,
            CONF_PORT: TEST_PORT,
            CONF_PATH: DEFAULT_PATH,
        },
        title="Dione",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_SCAN_INTERVAL: 30,
            CONF_ENABLE_DEVICE_SETTINGS_SENSORS: False,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {
        CONF_SCAN_INTERVAL: 30,
        CONF_ENABLE_DEVICE_SETTINGS_SENSORS: False,
    }
