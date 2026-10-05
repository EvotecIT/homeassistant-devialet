"""Entry ownership, retry, and subscription contracts through Home Assistant."""

from dataclasses import replace
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_BASE_URL


async def test_offline_startup_retries_without_publishing_runtime(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    session = async_get_clientsession(hass)
    aioclient_mock.get(f"{TEST_BASE_URL}/devices/current", status=503)

    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    assert not hasattr(mock_config_entry, "runtime_data")
    assert hass.states.get("media_player.dione") is None
    assert not session.closed

    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get("media_player.dione").state == "playing"
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert not session.closed


async def test_failed_unload_retains_owner_and_borrowed_session(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    owner = mock_config_entry.runtime_data
    session = async_get_clientsession(hass)

    with patch.object(
        hass.config_entries, "async_unload_platforms", AsyncMock(return_value=False)
    ):
        assert not await hass.config_entries.async_unload(mock_config_entry.entry_id)
    # HA versions differ in the failed-unload state; the retained owner is
    # the integration contract needed to keep remaining entities functional.
    assert mock_config_entry.runtime_data is owner
    assert not session.closed


async def test_reloads_preserve_entities_and_detach_old_coordinators(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    before = {
        entry.entity_id: entry.unique_id
        for entry in er.async_entries_for_config_entry(
            registry, mock_config_entry.entry_id
        )
    }
    previous_owners = []

    for _ in range(2):
        previous_owners.append(mock_config_entry.runtime_data)
        assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
        await hass.async_block_till_done()
        assert all(mock_config_entry.runtime_data is not old for old in previous_owners)
        assert {
            entry.entity_id: entry.unique_id
            for entry in er.async_entries_for_config_entry(
                registry, mock_config_entry.entry_id
            )
        } == before
        for old in previous_owners:
            old.async_set_updated_data(
                replace(old.data, volume=replace(old.data.volume, volume=1))
            )
        await hass.async_block_till_done()
        assert hass.states.get("media_player.dione").attributes["volume_level"] == 0.47

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_failed_platform_forwarding_can_retry_with_fresh_owner(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    failed_owners = []
    session = async_get_clientsession(hass)

    async def fail_forward(entry, platforms):
        failed_owners.append(entry.runtime_data)
        raise RuntimeError("Platform setup interrupted")

    with patch.object(hass.config_entries, "async_forward_entry_setups", fail_forward):
        assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert not session.closed
    assert hass.states.get("media_player.dione") is None

    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.runtime_data is not failed_owners[0]
    failed_owners[0].async_set_updated_data(
        replace(
            failed_owners[0].data,
            volume=replace(failed_owners[0].data.volume, volume=1),
        )
    )
    await hass.async_block_till_done()
    assert hass.states.get("media_player.dione").attributes["volume_level"] == 0.47
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert not session.closed
