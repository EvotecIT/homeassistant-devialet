"""Connection repair and rediscovery schedule one config-entry reload."""

from unittest.mock import AsyncMock

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.devialet import async_reload_entry
from custom_components.devialet.const import CONF_PATH, DEFAULT_PATH, DOMAIN
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import TEST_HOST, TEST_PORT, TEST_SERIAL


def _entry(hass, state, *, changed):
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
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return entry


@pytest.mark.parametrize("changed", [True, False])
@pytest.mark.parametrize(
    "state", [ConfigEntryState.LOADED, ConfigEntryState.NOT_LOADED]
)
async def test_reconfiguration_reloads_once(
    hass, monkeypatch, aioclient_mock, changed, state
):
    """Changed and unchanged repairs reload once with or without a listener."""
    entry = _entry(hass, state, changed=changed)
    old_identity = (entry.entry_id, entry.unique_id, entry.title)
    _mock_refresh_endpoints(aioclient_mock)
    reload = AsyncMock(return_value=True)
    monkeypatch.setattr(hass.config_entries, "async_reload", reload)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_RECONFIGURE,
                 "entry_id": entry.entry_id},
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
    entry = _entry(hass, state, changed=changed)
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

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=discovery
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == TEST_HOST
    if changed or state is ConfigEntryState.SETUP_RETRY:
        reload.assert_awaited_once_with(entry.entry_id)
    else:
        reload.assert_not_awaited()
