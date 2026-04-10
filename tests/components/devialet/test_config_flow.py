"""Config-flow tests for Devialet."""

from __future__ import annotations

import pytest
from aioresponses import aioresponses
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType

from custom_components.devialet.const import CONF_PATH, DEFAULT_PATH, DOMAIN
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


def _mock_refresh_endpoints(mocked: aioresponses) -> None:
    """Register the API endpoints used during validation and refresh."""
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
async def test_user_flow_creates_entry(hass) -> None:
    """Manual setup should validate the speaker and create an entry."""
    with aioresponses() as mocked:
        _mock_refresh_endpoints(mocked)
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
