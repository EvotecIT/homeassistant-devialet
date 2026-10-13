"""Borrowed HTTP session behavior against a local server."""

import asyncio
import gzip
import json
from contextlib import asynccontextmanager

import pytest
from aiohttp import ClientSession, TCPConnector, web

from custom_components.devialet.devialet_client.client import DevialetApiClient
from custom_components.devialet.devialet_client.const import (
    CURRENT_SOURCE_ENDPOINT,
    DEVICE_INFO_ENDPOINT,
    LED_MODE_ENDPOINT,
    NIGHT_MODE_ENDPOINT,
    POWER_MANAGEMENT_AUDIO_ENDPOINT,
    POWER_MANAGEMENT_ENDPOINT,
    RENDERING_MODE_ENDPOINT,
    SOURCES_ENDPOINT,
    SYSTEM_INFO_ENDPOINT,
    SYSTEM_VOLUME_ENDPOINT,
    VOLUME_ENDPOINT,
)
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
    VOLUME_PAYLOAD,
)

pytestmark = pytest.mark.usefixtures("socket_enabled")


@asynccontextmanager
async def local_server(handler):
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handler)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    try:
        await site.start()
        yield runner.addresses[0][1]
    finally:
        await runner.cleanup()


@pytest.mark.parametrize("raise_status", [False, True])
async def test_borrowed_status_policy_preserves_optional_volume_fallback(raise_status):
    paths = []

    async def handler(request):
        paths.append(request.path)
        if "/groups/" in request.path:
            return web.Response(status=404)
        return web.json_response({"volume": 42})

    async with (
        local_server(handler) as port,
        ClientSession(raise_for_status=raise_status) as session,
    ):
        client = DevialetApiClient("127.0.0.1", session, port=port)
        volume = await client.async_get_volume()
        assert volume.volume == 42
        assert paths == [
            "/ipcontrol/v1/groups/current/sources/current/soundControl/volume",
            "/ipcontrol/v1/systems/current/sources/current/soundControl/volume",
        ]
        assert not session.closed


@pytest.mark.parametrize("capabilities", ["complete", "none", "fallback"])
async def test_refresh_request_budget_and_connection_reuse(capabilities):
    """Repeated full polls release responses and reuse the caller's connection."""
    core = [DEVICE_INFO_ENDPOINT, SYSTEM_INFO_ENDPOINT, SOURCES_ENDPOINT,
            CURRENT_SOURCE_ENDPOINT, VOLUME_ENDPOINT]
    optional = [NIGHT_MODE_ENDPOINT, RENDERING_MODE_ENDPOINT, LED_MODE_ENDPOINT,
                POWER_MANAGEMENT_ENDPOINT]
    device = dict(DEVICE_PAYLOAD)
    system = dict(SYSTEM_PAYLOAD)
    if capabilities == "none":
        device["availableFeatures"] = system["availableFeatures"] = []
    payloads = dict(zip(core, [device, system, SOURCES_PAYLOAD,
                              CURRENT_SOURCE_PAYLOAD, VOLUME_PAYLOAD], strict=True))
    payloads.update(zip(optional, [NIGHT_MODE_PAYLOAD, RENDERING_MODE_PAYLOAD,
                                  LED_MODE_PAYLOAD, POWER_MANAGEMENT_PAYLOAD],
                        strict=True))
    payloads[SYSTEM_VOLUME_ENDPOINT] = VOLUME_PAYLOAD
    payloads[POWER_MANAGEMENT_AUDIO_ENDPOINT] = POWER_MANAGEMENT_PAYLOAD
    paths, connections = [], set()

    async def handler(request):
        endpoint = request.path.removeprefix("/ipcontrol/v1")
        paths.append(endpoint)
        connections.add(request.transport)
        if capabilities == "fallback" and endpoint in (
            VOLUME_ENDPOINT, POWER_MANAGEMENT_ENDPOINT,
        ):
            return web.Response(status=404)
        return web.json_response(payloads[endpoint])

    expected = core.copy()
    if capabilities == "fallback":
        expected.append(SYSTEM_VOLUME_ENDPOINT)
    if capabilities != "none":
        expected.extend(optional)
    if capabilities == "fallback":
        expected.append(POWER_MANAGEMENT_AUDIO_ENDPOINT)
    connector = TCPConnector(limit=1)
    async with (
        local_server(handler) as port,
        ClientSession(connector=connector) as session,
    ):
        client = DevialetApiClient("127.0.0.1", session, port=port)
        async with asyncio.timeout(5):
            for _ in range(6):
                snapshot = await client.async_refresh()
                assert snapshot.volume.volume == 47
                assert not connector._acquired
                assert not session.closed
        assert paths == expected * 6
        assert len(connections) == 1
    assert connector.closed


@pytest.mark.parametrize("operation", ["read", "write"])
@pytest.mark.parametrize("status", [404, 503])
async def test_power_management_fallback_requires_unsupported_endpoint(
    operation, status
):
    requests = []

    async def handler(request):
        body = await request.json() if request.method == "POST" else None
        requests.append((request.method, request.path, body))
        if "/audio/" not in request.path:
            return web.Response(status=status)
        return web.json_response({"autoPowerOff": "disabled", "autoPowerOffPeriod": 90})

    async with (
        local_server(handler) as port,
        ClientSession(raise_for_status=True) as session,
    ):
        client = DevialetApiClient("127.0.0.1", session, port=port)
        call = (
            client.async_get_power_management()
            if operation == "read"
            else client.async_set_auto_power_off_period(120)
        )
        if status == 503:
            with pytest.raises(DevialetResponseError, match="HTTP 503"):
                await call
            assert len(requests) == 1
        else:
            result = await call
            assert len(requests) == 2
            assert requests[1][1] == (
                "/ipcontrol/v1/systems/current/settings/audio/powerManagement"
            )
            if operation == "read":
                assert result.auto_power_off_period == 90
            else:
                assert requests[0][2] == requests[1][2] == {"autoPowerOffPeriod": 120}
        assert not session.closed


async def test_borrowed_session_decompression_policy_preserves_json_contract():
    async def handler(request):
        return web.Response(
            body=gzip.compress(json.dumps({"volume": 42}).encode()),
            headers={"Content-Encoding": "gzip"},
        )

    async with (
        local_server(handler) as port,
        ClientSession(auto_decompress=False) as session,
    ):
        volume = await DevialetApiClient(
            "127.0.0.1", session, port=port
        ).async_get_volume()
        assert volume.volume == 42
        assert not session.closed


@pytest.mark.parametrize(
    ("body", "code"),
    [("invalid-json", None), ("[]", None),
     ('{"error":{"code":"Rejected"}}', "Rejected"),
     ('{"error":{"code":42}}', None)],
)
async def test_malformed_and_api_error_responses_do_not_become_status(body, code):
    """A successful HTTP status is insufficient when the payload is invalid."""
    async def handler(request):
        return web.Response(text=body, content_type="application/json")

    async with local_server(handler) as port, ClientSession() as session:
        client = DevialetApiClient("127.0.0.1", session, port=port)
        with pytest.raises(DevialetResponseError) as caught:
            await client.async_get_volume()
        assert caught.value.status == 200
        assert caught.value.code == code
        assert not session.closed


@pytest.mark.parametrize("failure", ["disconnect", "timeout", "cancel"])
async def test_transport_failure_preserves_session_and_allows_next_request(failure):
    """Failed or cancelled reads leave the caller's session usable."""
    entered, release = asyncio.Event(), asyncio.Event()
    recovering = False

    async def handler(request):
        if not recovering:
            entered.set()
            if failure == "disconnect":
                request.transport.close()
            else:
                await release.wait()
        return web.json_response({"volume": 42})

    async with local_server(handler) as port, ClientSession() as session:
        client = DevialetApiClient(
            "127.0.0.1", session, port=port,
            request_timeout=0.1 if failure == "timeout" else 2,
        )
        try:
            if failure == "cancel":
                async with asyncio.TaskGroup() as tasks:
                    task = tasks.create_task(client.async_get_volume())
                    async with asyncio.timeout(2):
                        await entered.wait()
                    task.cancel()
                    with pytest.raises(asyncio.CancelledError):
                        await task
            else:
                with pytest.raises(DevialetConnectionError):
                    await client.async_get_volume()
            assert entered.is_set()
            assert not session.closed
        finally:
            recovering = True
            release.set()
        volume = await DevialetApiClient(
            "127.0.0.1", session, port=port
        ).async_get_volume()
        assert volume.volume == 42
