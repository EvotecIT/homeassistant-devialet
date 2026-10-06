"""Static-only installed API contract; this module is never executed."""

from typing import assert_type

from aiohttp import ClientSession

from devialet_client import DevialetApiClient, DevialetSnapshot
from devialet_client.client import DevialetApiClient as ModuleClient
from devialet_client.const import DEFAULT_PORT
from devialet_client.exceptions import DevialetConnectionError
from devialet_client.models import DevialetVolume


async def read(session: ClientSession) -> DevialetVolume | None:
    assert_type(DEFAULT_PORT, int)
    client = DevialetApiClient("127.0.0.1", session)
    assert_type(await client.async_refresh(), DevialetSnapshot)
    await client.async_set_volume_level("loud")  # type: ignore[arg-type]
    other: ModuleClient = client
    try:
        return await other.async_get_volume()
    except DevialetConnectionError:
        return None
