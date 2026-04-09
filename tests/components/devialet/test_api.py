"""Tests for the Devialet API client."""

from __future__ import annotations

from unittest.mock import AsyncMock

import aiohttp
import pytest

from custom_components.devialet.api import DevialetApiClient
from custom_components.devialet.const import (
    CURRENT_SOURCE_ENDPOINT,
    DEVICE_INFO_ENDPOINT,
    LED_MODE_ENDPOINT,
    NIGHT_MODE_ENDPOINT,
    POWER_MANAGEMENT_ENDPOINT,
    RENDERING_MODE_ENDPOINT,
    SOURCES_ENDPOINT,
    SYSTEM_INFO_ENDPOINT,
    VOLUME_ENDPOINT,
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
    TEST_HOST,
    VOLUME_PAYLOAD,
)


@pytest.mark.asyncio
async def test_async_refresh_builds_snapshot() -> None:
    """The client should build a typed snapshot from the current API surface."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    client = DevialetApiClient(TEST_HOST, session)

    responses = {
        DEVICE_INFO_ENDPOINT: DEVICE_PAYLOAD,
        SYSTEM_INFO_ENDPOINT: SYSTEM_PAYLOAD,
        SOURCES_ENDPOINT: SOURCES_PAYLOAD,
        CURRENT_SOURCE_ENDPOINT: CURRENT_SOURCE_PAYLOAD,
        VOLUME_ENDPOINT: VOLUME_PAYLOAD,
        NIGHT_MODE_ENDPOINT: NIGHT_MODE_PAYLOAD,
        RENDERING_MODE_ENDPOINT: RENDERING_MODE_PAYLOAD,
        LED_MODE_ENDPOINT: LED_MODE_PAYLOAD,
        POWER_MANAGEMENT_ENDPOINT: POWER_MANAGEMENT_PAYLOAD,
    }

    client._request_json = AsyncMock(  # type: ignore[method-assign]
        side_effect=lambda method, endpoint, payload=None: responses[endpoint]
    )

    snapshot = await client.async_refresh()

    assert snapshot.device.model == "Dione"
    assert snapshot.system.system_name == "Dione"
    assert len(snapshot.sources) == 6
    assert snapshot.volume.volume == 47
    assert snapshot.night_mode is not None
    assert snapshot.night_mode.night_mode is False
    assert snapshot.rendering_mode is not None
    assert snapshot.rendering_mode.rendering_mode == "movie"
    assert snapshot.led_mode is not None
    assert snapshot.led_mode.led_mode == "auto"
    assert snapshot.power_management is not None
    assert snapshot.power_management.auto_power_off_period == 90
    assert snapshot.source_state is not None
    assert snapshot.source_state.stream_info is not None
    assert snapshot.source_state.stream_info.codec == "pcm"


@pytest.mark.asyncio
async def test_async_set_rendering_mode_posts_expected_payload() -> None:
    """Rendering mode writes should follow the documented Devialet POST style."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    client = DevialetApiClient(TEST_HOST, session)
    client._request_json = AsyncMock(return_value={})  # type: ignore[method-assign]

    await client.async_set_rendering_mode("music")

    client._request_json.assert_awaited_once_with(
        "POST",
        RENDERING_MODE_ENDPOINT,
        payload={"renderingMode": "music"},
    )
