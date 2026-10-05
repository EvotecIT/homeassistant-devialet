"""Address formatting and HA action concurrency contracts."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import device_registry as dr

from custom_components.devialet.devialet_client.client import DevialetApiClient
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_BASE_URL, VOLUME_PAYLOAD


@pytest.mark.parametrize(
    ("host", "authority"),
    [
        ("192.0.2.10", "192.0.2.10"),
        ("speaker.local", "speaker.local"),
        ("2001:db8::10", "[2001:db8::10]"),
        ("[2001:db8::10]", "[2001:db8::10]"),
    ],
)
async def test_client_formats_request_and_configuration_urls(
    hass, aioclient_mock, host, authority
):
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    session = async_get_clientsession(hass)
    client = DevialetApiClient(host, session, port=8080, path="/api/test/")
    aioclient_mock.get(
        f"http://{authority}:8080/api/test/groups/current/sources/current/soundControl/volume",
        json=VOLUME_PAYLOAD,
    )
    volume = await client.async_get_volume()
    assert volume.volume == 47
    assert client.configuration_url == f"http://{authority}:8080"
    assert not session.closed


async def test_ipv6_device_registry_link_uses_client_url(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, data={**mock_config_entry.data, "host": "2001:db8::10"}
    )
    _mock_refresh_endpoints(
        aioclient_mock,
        base_url=TEST_BASE_URL.replace("192.0.2.10", "[2001:db8::10]"),
    )
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    devices = dr.async_entries_for_config_entry(
        dr.async_get(hass), mock_config_entry.entry_id
    )
    assert len(devices) == 1
    assert devices[0].configuration_url == "http://[2001:db8::10]:80"
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_multi_entity_switch_action_serializes_writes(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    active = 0
    maximum = 0
    completed = []

    async def write(value, **kwargs):
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        await asyncio.sleep(0)
        completed.append(value)
        active -= 1

    coordinator = mock_config_entry.runtime_data
    with (
        patch.object(coordinator.client, "async_set_night_mode", write),
        patch.object(coordinator.client, "async_set_auto_power_off_enabled", write),
        patch.object(coordinator, "async_request_refresh", AsyncMock()),
    ):
        await hass.services.async_call(
            "switch", "turn_on",
            {"entity_id": ["switch.dione_night_mode", "switch.dione_auto_power_off"]},
            blocking=True,
        )
    assert completed == [True, True]
    assert maximum == 1
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
