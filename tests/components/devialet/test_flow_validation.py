"""Public flow behavior for failed validation, discovery, and reconfiguration."""

from copy import deepcopy
from ipaddress import ip_address
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.translation import async_get_translations

from custom_components.devialet.const import (
    CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
    CONF_PATH,
    CONF_SCAN_INTERVAL,
    DEFAULT_PATH,
    DOMAIN,
)
from tests.components.devialet.test_init import _mock_refresh_endpoints
from tests.conftest import DEVICE_PAYLOAD, TEST_BASE_URL, TEST_HOST, TEST_PORT


def discovery(*, manufacturer="Devialet", serial=None):
    properties = {"manufacturer": manufacturer}
    if serial is not None:
        properties["serialNumber"] = serial
    return SimpleNamespace(
        host=ip_address(TEST_HOST), port=None, properties=properties,
        name="Living room._http._tcp.local.", type="_http._tcp.local.",
    )


async def start_flow(hass, kind, entry):
    if kind == "confirm":
        return await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF},
            data=discovery(),
        )
    context = {"source": kind}
    if kind == "reconfigure":
        context["entry_id"] = entry.entry_id
    return await hass.config_entries.flow.async_init(DOMAIN, context=context)


@pytest.mark.parametrize("kind", ["user", "confirm", "reconfigure"])
@pytest.mark.parametrize("failure", ["offline", "malformed", "missing_identity"])
async def test_failed_validation_preserves_entry_and_allows_retry(
    hass, aioclient_mock, mock_config_entry, kind, failure
):
    if kind == "reconfigure":
        mock_config_entry.add_to_hass(hass)
    original = dict(mock_config_entry.data)
    original_options = dict(mock_config_entry.options)
    if failure == "offline":
        aioclient_mock.get(f"{TEST_BASE_URL}/devices/current", status=503)
    elif failure == "malformed":
        aioclient_mock.get(f"{TEST_BASE_URL}/devices/current", text="not JSON")
    else:
        payload = {**DEVICE_PAYLOAD, "serial": None, "deviceId": None}
        _mock_refresh_endpoints(aioclient_mock, device_payload=payload)
    result = await start_flow(hass, kind, mock_config_entry)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == kind
    with patch.object(hass.config_entries, "async_reload", AsyncMock()) as reload:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {} if kind == "confirm" else {"host": TEST_HOST, "port": TEST_PORT},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == kind
        assert result["errors"] == {
            "base": "unsupported" if failure == "missing_identity" else "cannot_connect"
        }
        reload.assert_not_awaited()
    assert mock_config_entry.data == original
    assert mock_config_entry.options == original_options
    assert len(hass.config_entries.async_entries(DOMAIN)) == (kind == "reconfigure")


@pytest.mark.parametrize("wrong_device", [False, True])
async def test_reconfigure_validates_identity_before_address_update(
    hass, aioclient_mock, mock_config_entry, wrong_device
):
    mock_config_entry.add_to_hass(hass)
    original = dict(mock_config_entry.data)
    original_options = dict(mock_config_entry.options)
    new_host = "192.0.2.42"
    payload = deepcopy(DEVICE_PAYLOAD)
    if wrong_device:
        payload["serial"] = "different-device"
    _mock_refresh_endpoints(
        aioclient_mock, device_payload=payload,
        base_url=TEST_BASE_URL.replace(TEST_HOST, new_host),
    )
    result = await start_flow(hass, "reconfigure", mock_config_entry)
    with patch.object(hass.config_entries, "async_reload", AsyncMock()) as reload:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"host": new_host, "port": TEST_PORT}
        )
        await hass.async_block_till_done()
        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == (
            "wrong_device" if wrong_device else "reconfigure_successful"
        )
        if wrong_device:
            assert mock_config_entry.data == original
            reload.assert_not_awaited()
        else:
            assert mock_config_entry.data == {**original, "host": new_host}
            reload.assert_awaited_once_with(mock_config_entry.entry_id)
    assert mock_config_entry.options == original_options
    assert mock_config_entry.unique_id == DEVICE_PAYLOAD["serial"]


@pytest.mark.parametrize("kind", ["user", "confirm"])
async def test_same_device_discovered_or_entered_manually_is_not_duplicated(
    hass, aioclient_mock, mock_config_entry, kind
):
    mock_config_entry.add_to_hass(hass)
    _mock_refresh_endpoints(aioclient_mock)
    result = await start_flow(hass, kind, mock_config_entry)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {} if kind == "confirm" else {"host": TEST_HOST, "port": TEST_PORT},
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert hass.config_entries.async_entries(DOMAIN) == [mock_config_entry]


async def test_unrelated_discovery_is_rejected_before_network_request(
    hass, aioclient_mock
):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery(manufacturer="Other"),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unsupported"
    assert aioclient_mock.call_count == 0
    translations = await async_get_translations(hass, "en", "config", {DOMAIN})
    assert translations[f"component.{DOMAIN}.config.abort.unsupported"] == (
        "The discovered device does not advertise the Devialet IP Control API."
    )


@pytest.mark.parametrize("serial", [None, DEVICE_PAYLOAD["serial"]])
async def test_discovery_confirmation_uses_device_id_when_serial_is_absent(
    hass, aioclient_mock, serial
):
    payload = {**DEVICE_PAYLOAD, "serial": serial}
    _mock_refresh_endpoints(aioclient_mock, device_payload=payload)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery(serial=serial),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"
    with patch.object(hass.config_entries, "async_setup", AsyncMock(return_value=True)):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == (serial or DEVICE_PAYLOAD["deviceId"])
    assert result["data"] == {
        "host": TEST_HOST, "port": TEST_PORT, CONF_PATH: DEFAULT_PATH
    }


@pytest.mark.parametrize("interval", [2, 61])
async def test_invalid_polling_interval_does_not_change_options(
    hass, mock_config_entry, interval
):
    mock_config_entry.add_to_hass(hass)
    original = dict(mock_config_entry.options)
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    # Validate the form schema used by HA's frontend/websocket boundary.
    with pytest.raises(vol.Invalid):
        result["data_schema"]({
            CONF_SCAN_INTERVAL: interval,
            CONF_ENABLE_DEVICE_SETTINGS_SENSORS: True,
        })
    assert mock_config_entry.options == original


@pytest.mark.parametrize("kind", ["user", "reconfigure"])
@pytest.mark.parametrize("port", [-1, 65536])
async def test_network_form_rejects_out_of_range_ports(
    hass, mock_config_entry, kind, port
):
    if kind == "reconfigure":
        mock_config_entry.add_to_hass(hass)
    result = await start_flow(hass, kind, mock_config_entry)
    with pytest.raises(vol.Invalid):
        result["data_schema"]({"host": TEST_HOST, "port": port})
