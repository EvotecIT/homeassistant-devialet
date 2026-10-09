"""Connection repair and rediscovery schedule one config-entry reload."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState, DiscoveryKey
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.devialet import async_setup_entry
from custom_components.devialet.const import CONF_PATH, DEFAULT_PATH, DOMAIN
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_HOST, TEST_PORT, TEST_SERIAL


async def _entry(hass, monkeypatch, state, *, changed):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=TEST_SERIAL,
        title="Living Room",
        data={
            CONF_HOST: "192.0.2.99" if changed else TEST_HOST,
            CONF_PORT: TEST_PORT,
            CONF_PATH: DEFAULT_PATH,
        },
        options={"scan_interval": 45},
    )
    entry.add_to_hass(hass)
    entry.mock_state(hass, state)
    if state is ConfigEntryState.LOADED:
        coordinator = Mock(
            data=SimpleNamespace(device=SimpleNamespace(serial=TEST_SERIAL)),
            async_config_entry_first_refresh=AsyncMock(),
        )
        monkeypatch.setattr(
            "custom_components.devialet.DevialetCoordinator",
            Mock(return_value=coordinator),
        )
        monkeypatch.setattr(
            hass.config_entries, "async_forward_entry_setups", AsyncMock()
        )
        assert await async_setup_entry(hass, entry)
    return entry


@pytest.mark.parametrize("changed", [True, False])
@pytest.mark.parametrize(
    "state", [ConfigEntryState.LOADED, ConfigEntryState.NOT_LOADED]
)
async def test_reconfiguration_reloads_once(
    hass, monkeypatch, aioclient_mock, changed, state
):
    """Changed and unchanged repairs reload once with or without a listener."""
    entry = await _entry(hass, monkeypatch, state, changed=changed)
    old_identity = (entry.entry_id, entry.unique_id, entry.title)
    _mock_refresh_endpoints(aioclient_mock)
    reload = AsyncMock(return_value=True)
    monkeypatch.setattr(hass.config_entries, "async_reload", reload)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
        data={CONF_HOST: TEST_HOST, CONF_PORT: TEST_PORT},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    reload.assert_awaited_once_with(entry.entry_id)
    assert (entry.entry_id, entry.unique_id, entry.title) == old_identity
    assert entry.options == {"scan_interval": 45}
    assert entry.data[CONF_HOST] == TEST_HOST


@pytest.mark.parametrize("changed", [True, False])
@pytest.mark.parametrize(
    "state", [ConfigEntryState.LOADED, ConfigEntryState.SETUP_RETRY]
)
async def test_rediscovery_reloads_once(hass, monkeypatch, changed, state):
    """Discovery updates a loaded speaker or wakes a retrying entry once."""
    entry = await _entry(hass, monkeypatch, state, changed=changed)
    reload = AsyncMock(return_value=True)
    monkeypatch.setattr(hass.config_entries, "async_reload", reload)
    discovery = ZeroconfServiceInfo(
        ip_address=TEST_HOST,
        ip_addresses=[TEST_HOST],
        hostname="dione.local.",
        type="_http._tcp.local.",
        name="Living Room._http._tcp.local.",
        port=TEST_PORT,
        properties={"manufacturer": "Devialet", "serialNumber": TEST_SERIAL},
    )

    discovery_key = DiscoveryKey(
        domain="zeroconf", key=(discovery.type, discovery.name), version=1
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_ZEROCONF,
            "discovery_key": discovery_key,
        },
        data=discovery,
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == TEST_HOST
    assert discovery_key in entry.discovery_keys["zeroconf"]
    if changed or state is ConfigEntryState.SETUP_RETRY:
        reload.assert_awaited_once_with(entry.entry_id)
    else:
        reload.assert_not_awaited()


@pytest.mark.parametrize("field", ["data", "options", "title", "unique_id"])
async def test_registered_listener_preserves_setting_reload(hass, monkeypatch, field):
    """Settings and naming changes retain the registered listener's reload."""
    entry = await _entry(hass, monkeypatch, ConfigEntryState.LOADED, changed=False)
    reload = AsyncMock(return_value=True)
    monkeypatch.setattr(hass.config_entries, "async_reload", reload)
    value = {
        "data": {**entry.data, CONF_HOST: "new-speaker.local"},
        "options": {**entry.options, "scan_interval": 60},
        "title": "Renamed speaker",
        "unique_id": "changed-speaker-id",
    }[field]

    hass.config_entries.async_update_entry(entry, **{field: value})
    await hass.async_block_till_done()

    reload.assert_awaited_once_with(entry.entry_id)


@pytest.mark.parametrize("first_refresh_fails", [False, True])
async def test_rediscovery_during_setup_uses_new_host(
    hass, monkeypatch, first_refresh_fails
):
    """Discovery reloads after the active setup lock, including failed refresh."""
    entry = await _entry(hass, monkeypatch, ConfigEntryState.NOT_LOADED, changed=True)
    entered, release = asyncio.Event(), asyncio.Event()
    setup_hosts, unload_states = [], []

    async def first_refresh():
        entered.set()
        await release.wait()
        if first_refresh_fails:
            raise ConfigEntryNotReady("Old speaker address is unavailable")

    def coordinator_factory(_hass, setup_entry):
        setup_hosts.append(setup_entry.data[CONF_HOST])
        return Mock(
            data=SimpleNamespace(device=SimpleNamespace(serial=TEST_SERIAL)),
            async_config_entry_first_refresh=AsyncMock(
                side_effect=first_refresh if len(setup_hosts) == 1 else None
            ),
        )

    monkeypatch.setattr(
        "custom_components.devialet.DevialetCoordinator", coordinator_factory
    )
    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", AsyncMock())
    monkeypatch.setattr(
        hass.config_entries, "async_unload_platforms", AsyncMock(return_value=True)
    )
    reload = AsyncMock(wraps=hass.config_entries.async_reload)
    monkeypatch.setattr(hass.config_entries, "async_reload", reload)
    original_unload = hass.config_entries.async_unload

    async def unload(*args, **kwargs):
        unload_states.append(entry.state)
        return await original_unload(*args, **kwargs)

    monkeypatch.setattr(hass.config_entries, "async_unload", unload)
    task = hass.async_create_task(hass.config_entries.async_setup(entry.entry_id))
    await asyncio.wait_for(entered.wait(), timeout=10)
    discovery = ZeroconfServiceInfo(
        ip_address=TEST_HOST, ip_addresses=[TEST_HOST], hostname="dione.local.",
        type="_http._tcp.local.", name="Living Room._http._tcp.local.", port=TEST_PORT,
        properties={"manufacturer": "Devialet", "serialNumber": TEST_SERIAL},
    )
    try:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_ZEROCONF,
                "discovery_key": DiscoveryKey(
                    domain="zeroconf", key=(discovery.type, discovery.name), version=1
                ),
            },
            data=discovery,
        )
        assert result["reason"] == "already_configured"
        assert entry.state is ConfigEntryState.SETUP_IN_PROGRESS
    finally:
        release.set()
    await task
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    assert setup_hosts == ["192.0.2.99", TEST_HOST]
    assert unload_states == [
        ConfigEntryState.SETUP_RETRY if first_refresh_fails else ConfigEntryState.LOADED
    ]
    reload.assert_awaited_once_with(entry.entry_id)
    assert len(entry.update_listeners) == 1
