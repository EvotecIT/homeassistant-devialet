"""Saved speaker identity must survive address reuse and recovery."""

import asyncio
from dataclasses import replace
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.translation import async_get_translations

from custom_components.devialet.const import DOMAIN
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import DEVICE_PAYLOAD, TEST_BASE_URL, TEST_DEVICE_ID, TEST_HOST


async def test_setup_rejects_reassigned_address_without_creating_entities(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(
        aioclient_mock,
        device_payload={**DEVICE_PAYLOAD, "serial": "OTHER-SPEAKER",
                        "deviceId": "other-device"},
    )

    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert not hasattr(mock_config_entry, "runtime_data")
    assert hass.states.get("media_player.dione") is None
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"device_identity_{mock_config_entry.entry_id}"
    )
    assert issue is not None and issue.translation_key == "wrong_device"

    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get("media_player.dione").state == "playing"
    assert ir.async_get(hass).async_get_issue(
        DOMAIN, f"device_identity_{mock_config_entry.entry_id}"
    ) is None
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_changed_identity_blocks_actions_and_retains_original_registry(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    owner = mock_config_entry.runtime_data
    original = owner.data
    entities = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    devices = dr.async_entries_for_config_entry(
        dr.async_get(hass), mock_config_entry.entry_id
    )
    before = {e.entity_id: e.unique_id for e in entities}
    before_devices = {d.id: d.identifiers for d in devices}
    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(
        aioclient_mock,
        device_payload={**DEVICE_PAYLOAD, "serial": "OTHER-SPEAKER",
                        "deviceId": "other-device"},
    )
    await owner.async_refresh()
    await hass.async_block_till_done()
    assert not owner.last_update_success and not owner.identity_matches_entry
    assert owner.data is original
    assert hass.states.get("media_player.dione").state == "unavailable"
    assert {e.entity_id: e.unique_id for e in er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )} == before
    assert {d.id: d.identifiers for d in dr.async_entries_for_config_entry(
        dr.async_get(hass), mock_config_entry.entry_id
    )} == before_devices
    aioclient_mock.post(
        f"{TEST_BASE_URL}/groups/current/sources/current/soundControl/volume",
        json={},
    )
    calls = len(aioclient_mock.mock_calls)
    await hass.services.async_call(
        "media_player", "volume_set",
        {"entity_id": "media_player.dione", "volume_level": 0.2},
        blocking=True,
    )
    assert len(aioclient_mock.mock_calls) == calls
    # HA ignores unavailable service targets. A retained entity action must
    # also reject before I/O rather than acting on the replacement speaker.
    entity = hass.data["media_player"].get_entity("media_player.dione")
    with pytest.raises(HomeAssistantError) as error:
        await entity.async_set_volume_level(0.2)
    assert error.value.translation_key == "wrong_device"
    assert len(aioclient_mock.mock_calls) == calls

    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(aioclient_mock)
    await owner.async_refresh()
    await hass.async_block_till_done()
    assert owner.last_update_success and owner.identity_matches_entry
    assert hass.states.get("media_player.dione").state == "playing"
    assert ir.async_get(hass).async_get_issue(
        DOMAIN, f"device_identity_{mock_config_entry.entry_id}"
    ) is None
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_removing_failed_entry_clears_its_repair(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(
        aioclient_mock, device_payload={**DEVICE_PAYLOAD, "serial": "other"},
    )
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    issue_id = f"device_identity_{mock_config_entry.entry_id}"
    assert ir.async_get(hass).async_get_issue(DOMAIN, issue_id) is not None
    assert await hass.config_entries.async_remove(mock_config_entry.entry_id)
    assert ir.async_get(hass).async_get_issue(DOMAIN, issue_id) is None


@pytest.mark.parametrize("language", ["en", "pl", "fr"])
async def test_identity_repair_and_error_have_translated_guidance(hass, language):
    for category in ("issues", "exceptions"):
        translations = await async_get_translations(
            hass, language, category, {DOMAIN}
        )
        prefix = f"component.devialet.{category}.wrong_device."
        assert translations[prefix + ("title" if category == "issues" else "message")]
        if category == "issues":
            assert translations[prefix + "description"]


@pytest.mark.parametrize("operation", ["reload", "remove", "reload_preserve"])
async def test_inflight_old_refresh_cannot_change_current_repair(
    hass, mock_config_entry, aioclient_mock, operation
):
    """Refreshes finishing after lifecycle transitions cannot mutate global state."""
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    owner = mock_config_entry.runtime_data
    wrong = replace(owner.data, device=replace(
        owner.data.device, serial="another-speaker", device_id="another-device"
    ))
    delayed_snapshot = owner.data if operation == "reload_preserve" else wrong
    entered, release = asyncio.Event(), asyncio.Event()

    async def delayed():
        entered.set()
        await release.wait()
        return delayed_snapshot

    async with asyncio.TaskGroup() as tasks:
        with patch.object(owner.client, "async_refresh", delayed):
            task = tasks.create_task(owner.async_request_refresh())
            try:
                async with asyncio.timeout(5):
                    await entered.wait()
                if operation == "reload_preserve":
                    aioclient_mock.clear_requests()
                    _mock_refresh_endpoints(
                        aioclient_mock,
                        device_payload={**DEVICE_PAYLOAD, "serial": "another-speaker",
                                        "deviceId": "another-device"},
                    )
                    assert not await hass.config_entries.async_reload(
                        mock_config_entry.entry_id
                    )
                elif operation == "reload":
                    assert await hass.config_entries.async_reload(
                        mock_config_entry.entry_id
                    )
                    assert mock_config_entry.runtime_data is not owner
                else:
                    assert await hass.config_entries.async_remove(
                        mock_config_entry.entry_id
                    )
            finally:
                release.set()
            await task
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"device_identity_{mock_config_entry.entry_id}"
    )
    assert (issue is not None) == (operation == "reload_preserve")
    assert not owner.identity_matches_entry
    if operation == "reload":
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)


async def test_fallback_identity_survives_serial_arrival_and_reconfigure(
    hass, mock_config_entry, aioclient_mock
):
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(mock_config_entry, unique_id=TEST_DEVICE_ID)
    _mock_refresh_endpoints(
        aioclient_mock, device_payload={**DEVICE_PAYLOAD, "serial": None},
    )
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    devices = dr.async_get(hass)
    before = {e.entity_id: e.unique_id for e in er.async_entries_for_config_entry(
        registry, mock_config_entry.entry_id
    )}
    before_devices = {d.id: d.identifiers for d in dr.async_entries_for_config_entry(
        devices, mock_config_entry.entry_id
    )}
    aioclient_mock.clear_requests()
    _mock_refresh_endpoints(aioclient_mock)
    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.runtime_data.identity_matches_entry
    assert {e.entity_id: e.unique_id for e in er.async_entries_for_config_entry(
        registry, mock_config_entry.entry_id
    )} == before
    assert {d.id: d.identifiers for d in dr.async_entries_for_config_entry(
        devices, mock_config_entry.entry_id
    )} == before_devices
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE,
                         "entry_id": mock_config_entry.entry_id},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"host": TEST_HOST, "port": 80},
    )
    await hass.async_block_till_done()
    assert result["type"] == "abort" and result["reason"] == "reconfigure_successful"
    assert mock_config_entry.unique_id == TEST_DEVICE_ID
    # Manual setup must recognize the same alias and must not create a duplicate.
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"host": TEST_HOST, "port": 80},
    )
    assert result["type"] == "abort" and result["reason"] == "already_configured"
    assert hass.config_entries.async_entries(DOMAIN) == [mock_config_entry]
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
